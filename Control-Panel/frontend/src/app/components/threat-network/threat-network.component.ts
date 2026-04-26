import {
  AfterViewInit,
  Component,
  DestroyRef,
  ElementRef,
  NgZone,
  computed,
  inject,
  signal,
  viewChild
} from '@angular/core';
import { animate, stagger } from 'animejs';
import * as d3 from 'd3';

type ThreatMessage = {
  channel: string;
  text: string;
  timestamp: string;
};

type NodeRole = 'recruiter' | 'hub' | 'bridge' | 'target' | 'observer';

type ThreatNode = {
  id: string;
  clusterId: string;
  role: NodeRole;
  radius: number;
  anchorX: number;
  anchorY: number;
  userName: string;
  handle: string;
  platform: string;
  publications: number;
  loadMethod: string;
  loadProgress: number;
  scrapingValue: number;
  relationScore: number;
  summary: string;
  centrality: number;
  messages: ThreatMessage[];
};

type ThreatLink = {
  source: string;
  target: string;
  strength: number;
};

type PositionedThreatNode = ThreatNode & {
  x: number;
  y: number;
  originX: number;
  originY: number;
  layer: number;
};

type PositionedThreatLink = ThreatLink & {
  sourceNode: PositionedThreatNode;
  targetNode: PositionedThreatNode;
};

type RawNode = Omit<ThreatNode, 'centrality'>;

@Component({
  selector: 'app-threat-network',
  templateUrl: './threat-network.component.html',
  styleUrl: './threat-network.component.css'
})
export class ThreatNetworkComponent implements AfterViewInit {
  private readonly host = viewChild.required<ElementRef<HTMLElement>>('networkHost');
  private readonly detailPanel = viewChild.required<ElementRef<HTMLElement>>('detailPanel');
  private readonly messageStream = viewChild.required<ElementRef<HTMLElement>>('messageStream');
  private readonly destroyRef = inject(DestroyRef);
  private readonly ngZone = inject(NgZone);
  private resizeObserver?: ResizeObserver;
  private cleanupGraph?: () => void;
  private pendingRenderFrame?: number;
  private updateSelectionState?: (selectedId: string | null) => void;
  private lastRenderWidth = 0;
  private lastRenderHeight = 0;

  private readonly graphData = this.buildGraphData();
  private readonly nodes = this.graphData.nodes;
  private readonly links = this.graphData.links;
  private readonly nodeIndex = new Map(this.nodes.map((node) => [node.id, node]));
  private readonly adjacency = this.buildAdjacency(this.links);

  protected readonly selectedNodeId = signal(this.nodes[0]?.id ?? '');
  protected readonly detailOpen = signal(false);
  protected readonly selectedNode = computed(
    () => this.nodeIndex.get(this.selectedNodeId()) ?? this.nodes[0]
  );
  protected readonly selectedRelationLabel = computed(() =>
    this.getRelationLabel(this.selectedNode().relationScore)
  );
  protected readonly recruiterCount = this.nodes.filter((node) => node.role === 'recruiter').length;

  ngAfterViewInit(): void {
    const host = this.host().nativeElement;
    this.scheduleRender(host, true);

    this.resizeObserver = new ResizeObserver(() => {
      this.scheduleRender(host);
    });

    this.resizeObserver.observe(host);
    this.destroyRef.onDestroy(() => {
      this.resizeObserver?.disconnect();
      if (this.pendingRenderFrame !== undefined) {
        cancelAnimationFrame(this.pendingRenderFrame);
      }
      this.cleanupGraph?.();
    });
  }

  protected closeDetail(): void {
    this.detailOpen.set(false);
    this.updateSelectionState?.(null);
  }

  protected getRelationColor(score: number): string {
    if (score <= 20) return '#f4f6fb';
    if (score <= 45) return '#85f1b1';
    if (score <= 75) return '#ffd27c';
    return '#ff7269';
  }

  private scheduleRender(host: HTMLElement, force = false): void {
    if (this.pendingRenderFrame !== undefined) {
      cancelAnimationFrame(this.pendingRenderFrame);
    }

    this.pendingRenderFrame = requestAnimationFrame(() => {
      this.pendingRenderFrame = undefined;

      const width = Math.round(host.clientWidth || 1280);
      const height = Math.round(host.clientHeight || 780);
      if (!force && width === this.lastRenderWidth && height === this.lastRenderHeight) {
        return;
      }

      this.lastRenderWidth = width;
      this.lastRenderHeight = height;
      this.renderGraph(host, width, height);
    });
  }

  private renderGraph(host: HTMLElement, width: number, height: number): void {
    this.cleanupGraph?.();
    this.updateSelectionState = undefined;

    const worldWidth = Math.max(width * 1.35, 1600);
    const worldHeight = Math.max(height * 1.2, 1050);
    const positionedNodes = this.nodes.map((node) => {
      const originX = worldWidth * node.anchorX;
      const originY = worldHeight * node.anchorY;

      return {
        ...node,
        x: originX,
        y: originY,
        originX,
        originY,
        layer: this.getNodeLayer(node.role)
      };
    });
    const nodePositions = new Map(positionedNodes.map((node) => [node.id, node] as const));
    const positionedLinks = this.links.flatMap((link) => {
      const sourceNode = nodePositions.get(link.source);
      const targetNode = nodePositions.get(link.target);
      return sourceNode && targetNode ? [{ ...link, sourceNode, targetNode }] : [];
    });

    d3.select(host).selectAll('svg').remove();
    host.style.touchAction = 'none';
    host.style.userSelect = 'none';

    const svg = d3
      .select(host)
      .append('svg')
      .attr('viewBox', `0 0 ${width} ${height}`)
      .style('width', '100%')
      .style('height', '100%')
      .style('touch-action', 'none')
      .style('cursor', 'grab')
      .attr('aria-label', 'Grafo de relaciones probabilistas');

    const defs = svg.append('defs');
    const gridPattern = defs
      .append('pattern')
      .attr('id', 'network-grid')
      .attr('width', 72)
      .attr('height', 72)
      .attr('patternUnits', 'userSpaceOnUse');

    gridPattern
      .append('path')
      .attr('d', 'M 72 0 L 0 0 0 72')
      .attr('fill', 'none')
      .attr('stroke', 'rgba(124, 155, 209, 0.06)')
      .attr('stroke-width', 1);

    const zoomLayer = svg.append('g');
    zoomLayer
      .append('rect')
      .attr('width', worldWidth)
      .attr('height', worldHeight)
      .attr('fill', 'url(#network-grid)');

    const auraLayer = zoomLayer.append('g').attr('opacity', 0.7);
    auraLayer
      .append('circle')
      .attr('cx', worldWidth * 0.16)
      .attr('cy', worldHeight * 0.24)
      .attr('r', 220)
      .attr('fill', 'rgba(124, 232, 255, 0.05)');
    auraLayer
      .append('circle')
      .attr('cx', worldWidth * 0.46)
      .attr('cy', worldHeight * 0.38)
      .attr('r', 260)
      .attr('fill', 'rgba(255, 114, 105, 0.04)');
    auraLayer
      .append('circle')
      .attr('cx', worldWidth * 0.77)
      .attr('cy', worldHeight * 0.26)
      .attr('r', 240)
      .attr('fill', 'rgba(255, 210, 124, 0.045)');
    auraLayer
      .append('circle')
      .attr('cx', worldWidth * 0.66)
      .attr('cy', worldHeight * 0.74)
      .attr('r', 260)
      .attr('fill', 'rgba(133, 241, 177, 0.04)');

    const linkSelection = zoomLayer
      .append('g')
      .selectAll<SVGLineElement, PositionedThreatLink>('line')
      .data(positionedLinks)
      .join('line')
      .attr('stroke', (d: PositionedThreatLink) => this.getRelationColor(d.strength * 100))
      .attr('stroke-opacity', 0.72)
      .attr('stroke-linecap', 'round')
      .attr('stroke-width', (d: PositionedThreatLink) => 1.4 + d.strength * 5)
      .attr('x1', (d: PositionedThreatLink) => d.sourceNode.x)
      .attr('y1', (d: PositionedThreatLink) => d.sourceNode.y)
      .attr('x2', (d: PositionedThreatLink) => d.targetNode.x)
      .attr('y2', (d: PositionedThreatLink) => d.targetNode.y);

    const haloSelection = zoomLayer
      .append('g')
      .selectAll<SVGCircleElement, PositionedThreatNode>('circle')
      .data(positionedNodes)
      .join('circle')
      .attr('r', (d) => d.radius + (d.role === 'recruiter' ? 14 : 7))
      .attr('cx', (d) => d.x)
      .attr('cy', (d) => d.y)
      .attr('fill', (d) =>
        d.role === 'recruiter' ? 'rgba(255, 114, 105, 0.14)' : 'rgba(124, 232, 255, 0.08)'
      )
      .attr('pointer-events', 'none');

    const nodeSelection = zoomLayer
      .append('g')
      .selectAll<SVGCircleElement, PositionedThreatNode>('circle')
      .data(positionedNodes)
      .join('circle')
      .attr('r', (d) => d.radius)
      .attr('cx', (d) => d.x)
      .attr('cy', (d) => d.y)
      .attr('fill', (d) => this.getNodeColor(d.role))
      .attr('stroke', '#04111d')
      .attr('stroke-width', (d) => (d.role === 'recruiter' ? 3.2 : 2))
      .style('cursor', 'pointer');

    const labelSelection = zoomLayer
      .append('g')
      .selectAll<SVGTextElement, PositionedThreatNode>('text')
      .data(positionedNodes)
      .join('text')
      .text((d) => d.userName)
      .attr('x', (d) => d.x)
      .attr('y', (d) => d.y + d.radius + 24)
      .attr('fill', '#eff7ff')
      .attr('font-size', (d) => (d.role === 'recruiter' ? 13 : 11))
      .attr('font-weight', (d) => (d.role === 'recruiter' ? 700 : 600))
      .attr('text-anchor', 'middle')
      .attr('paint-order', 'stroke')
      .attr('stroke', 'rgba(2, 8, 14, 0.94)')
      .attr('stroke-width', 4)
      .attr('stroke-linejoin', 'round')
      .attr('pointer-events', 'none');

    let currentScale = 1;
    let currentTransform = d3.zoomIdentity;
    let pendingPositionFrame: number | undefined;
    const returnAnimationFrames = new Map<string, number>();

    const updateGraphPositions = (): void => {
      linkSelection
        .attr('x1', (d) => d.sourceNode.x)
        .attr('y1', (d) => d.sourceNode.y)
        .attr('x2', (d) => d.targetNode.x)
        .attr('y2', (d) => d.targetNode.y);

      haloSelection.attr('cx', (d) => d.x).attr('cy', (d) => d.y);
      nodeSelection.attr('cx', (d) => d.x).attr('cy', (d) => d.y);
      labelSelection.attr('x', (d) => d.x).attr('y', (d) => d.y + d.radius + 24);
    };

    const scheduleGraphPositionUpdate = (): void => {
      if (pendingPositionFrame !== undefined) {
        return;
      }

      pendingPositionFrame = requestAnimationFrame(() => {
        pendingPositionFrame = undefined;
        updateGraphPositions();
      });
    };

    const getVisibleLayer = (): number => {
      if (currentScale >= 1.08) return 4;
      if (currentScale >= 0.88) return 3;
      if (currentScale >= 0.7) return 2;
      return 1;
    };

    const shouldPreserveNode = (selectedId: string | null, nodeId: string): boolean =>
      !!selectedId && this.isNodeConnected(selectedId, nodeId);

    const updateLayerCompression = (selectedId: string | null): void => {
      const visibleLayer = getVisibleLayer();
      const showHalos = currentScale >= 0.88 && positionedNodes.length <= 180;
      const showDenseLabels = currentScale >= 0.98 || positionedNodes.length <= 34;

      nodeSelection.attr('display', (d) =>
        d.layer <= visibleLayer || shouldPreserveNode(selectedId, d.id) ? null : 'none'
      );

      haloSelection.attr('display', (d) =>
        showHalos && (d.layer <= visibleLayer || shouldPreserveNode(selectedId, d.id)) ? null : 'none'
      );

      labelSelection.attr('display', (d) => {
        if (shouldPreserveNode(selectedId, d.id)) {
          return null;
        }

        if (showDenseLabels) {
          return d.layer <= visibleLayer ? null : 'none';
        }

        return d.layer <= Math.min(visibleLayer, 1) ? null : 'none';
      });

      linkSelection.attr('display', (d) => {
        const sourceVisible = d.sourceNode.layer <= visibleLayer || shouldPreserveNode(selectedId, d.sourceNode.id);
        const targetVisible = d.targetNode.layer <= visibleLayer || shouldPreserveNode(selectedId, d.targetNode.id);
        return sourceVisible && targetVisible ? null : 'none';
      });
    };

    const animateNodeBack = (node: PositionedThreatNode): void => {
      const activeFrame = returnAnimationFrames.get(node.id);
      if (activeFrame !== undefined) {
        cancelAnimationFrame(activeFrame);
      }

      const startX = node.x;
      const startY = node.y;
      const startTime = performance.now();
      const duration = 220;

      const step = (now: number): void => {
        const progress = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);

        node.x = startX + (node.originX - startX) * eased;
        node.y = startY + (node.originY - startY) * eased;
        scheduleGraphPositionUpdate();

        if (progress < 1) {
          returnAnimationFrames.set(node.id, requestAnimationFrame(step));
          return;
        }

        node.x = node.originX;
        node.y = node.originY;
        scheduleGraphPositionUpdate();
        returnAnimationFrames.delete(node.id);
      };

      returnAnimationFrames.set(node.id, requestAnimationFrame(step));
    };

    const applySelectionState = (selectedId: string | null): void => {
      updateLayerCompression(selectedId);

      nodeSelection
        .attr('opacity', (d) => (!selectedId || this.isNodeConnected(selectedId, d.id) ? 1 : 0.18))
        .attr('stroke', (d) => (d.id === selectedId ? '#ffffff' : '#04111d'))
        .attr('stroke-width', (d) => (d.id === selectedId ? 4.2 : d.role === 'recruiter' ? 3.2 : 2));

      haloSelection.attr('opacity', (d) => (!selectedId || this.isNodeConnected(selectedId, d.id) ? 1 : 0.1));

      linkSelection
        .attr('stroke-opacity', (d) => (!selectedId ? 0.72 : this.linkTouchesNode(d, selectedId) ? 0.96 : 0.08))
        .attr('stroke-width', (d) =>
          (selectedId && this.linkTouchesNode(d, selectedId) ? 2.3 : 1.1) + d.strength * 4.5
        );

      labelSelection
        .attr('opacity', (d) => (!selectedId || this.isNodeConnected(selectedId, d.id) ? 1 : 0.2))
        .attr('fill', (d) => (d.id === selectedId ? '#ffffff' : '#eff7ff'));
    };

    const openNodeDetail = (node: PositionedThreatNode): void => {
      this.ngZone.run(() => {
        this.selectedNodeId.set(node.id);
        this.detailOpen.set(true);
        applySelectionState(node.id);
        this.animateSelectionPanel();
      });
    };

    const drag = d3
      .drag<SVGCircleElement, PositionedThreatNode>()
      .container(() => svg.node() as SVGSVGElement)
      .clickDistance(6)
      .on('start', (event, node) => {
        event.sourceEvent.stopPropagation();
        const activeFrame = returnAnimationFrames.get(node.id);
        if (activeFrame !== undefined) {
          cancelAnimationFrame(activeFrame);
          returnAnimationFrames.delete(node.id);
        }
        svg.style('cursor', 'grabbing');
      })
      .on('drag', (event, node) => {
        const [nextX, nextY] = currentTransform.invert([event.x, event.y]);
        const padding = node.radius + 22;

        node.x = this.clamp(nextX, padding, worldWidth - padding);
        node.y = this.clamp(nextY, padding, worldHeight - padding);
        scheduleGraphPositionUpdate();
      })
      .on('end', (event, node) => {
        event.sourceEvent.stopPropagation();
        svg.style('cursor', 'grab');
        animateNodeBack(node);
      });

    nodeSelection.call(drag);

    nodeSelection.on('click', (event: MouseEvent, node) => {
      if (event.defaultPrevented) {
        return;
      }

      openNodeDetail(node);
    });

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.45, 2.6])
      .on('zoom', (event: d3.D3ZoomEvent<SVGSVGElement, unknown>) => {
        currentTransform = event.transform;
        currentScale = event.transform.k;
        zoomLayer.attr('transform', event.transform.toString());
        applySelectionState(this.detailOpen() ? this.selectedNodeId() : null);
      });

    svg.call(zoom);

    const initialScale = Math.max(0.58, Math.min(width / worldWidth, height / worldHeight) * 1.06);
    const initialTransform = d3.zoomIdentity
      .translate((width - worldWidth * initialScale) / 2, (height - worldHeight * initialScale) / 2)
      .scale(initialScale);

    currentTransform = initialTransform;
    currentScale = initialScale;
    svg.call(zoom.transform, initialTransform);
    applySelectionState(this.detailOpen() ? this.selectedNodeId() : null);
    this.updateSelectionState = applySelectionState;

    this.cleanupGraph = () => {
      this.updateSelectionState = undefined;
      if (pendingPositionFrame !== undefined) {
        cancelAnimationFrame(pendingPositionFrame);
      }
      for (const frameId of returnAnimationFrames.values()) {
        cancelAnimationFrame(frameId);
      }
      svg.remove();
    };
  }

  private animateSelectionPanel(): void {
    requestAnimationFrame(() => {
      if (!this.detailOpen()) {
        return;
      }

      const detailPanel = this.detailPanel().nativeElement;
      const messageStream = this.messageStream().nativeElement;

      animate(detailPanel.querySelectorAll('.detail-card, .metric-card, .panel-heading, .detail-progress'), {
        opacity: [0, 1],
        x: [22, 0],
        duration: 420,
        delay: stagger(55),
        ease: 'outExpo'
      });

      animate(detailPanel.querySelectorAll('.progress-fill, .scraping-fill'), {
        scaleX: [0, 1],
        duration: 620,
        delay: stagger(80, { start: 80 }),
        ease: 'outCubic'
      });

      animate(messageStream.querySelectorAll('.message-item'), {
        opacity: [0, 1],
        x: [18, 0],
        duration: 520,
        delay: stagger(90, { start: 120 }),
        ease: 'outExpo'
      });
    });
  }

  private isNodeConnected(selectedId: string, nodeId: string): boolean {
    return selectedId === nodeId || this.adjacency.get(selectedId)?.has(nodeId) === true;
  }

  private linkTouchesNode(link: ThreatLink, nodeId: string): boolean {
    return link.source === nodeId || link.target === nodeId;
  }

  private getRelationLabel(score: number): string {
    if (score <= 20) return 'Relacion debil';
    if (score <= 45) return 'Relacion baja';
    if (score <= 75) return 'Relacion moderada';
    return 'Relacion alta';
  }

  private getNodeColor(role: NodeRole): string {
    if (role === 'recruiter') return '#ff7269';
    if (role === 'hub') return '#ffd27c';
    if (role === 'bridge') return '#7ce8ff';
    if (role === 'target') return '#dce5f6';
    return '#97f7c1';
  }

  private buildAdjacency(links: ThreatLink[]): Map<string, Set<string>> {
    const adjacency = new Map<string, Set<string>>();

    for (const link of links) {
      if (!adjacency.has(link.source)) {
        adjacency.set(link.source, new Set<string>());
      }
      if (!adjacency.has(link.target)) {
        adjacency.set(link.target, new Set<string>());
      }

      adjacency.get(link.source)?.add(link.target);
      adjacency.get(link.target)?.add(link.source);
    }

    return adjacency;
  }

  private getNodeLayer(role: NodeRole): number {
    if (role === 'recruiter') return 0;
    if (role === 'hub') return 1;
    if (role === 'bridge') return 2;
    if (role === 'target') return 3;
    return 4;
  }

  private clamp(value: number, min: number, max: number): number {
    return Math.min(Math.max(value, min), max);
  }

  private buildGraphData(): { nodes: ThreatNode[]; links: ThreatLink[] } {
    const rawNodes: RawNode[] = [
      this.createNode('north-r0', 'north', 'recruiter', 0.14, 0.2, 'Ariadna Vela', '@ariadna.v', 'TikTok', 264, 'Scraping continuo', 96, 91, 88, 'Recruiter del cluster norte con alta concentracion de nodos satelite.', [
        this.createMessage('Comentario', 'Concentra respuestas de ocho nodos secundarios.', 'Hace 9 s'),
        this.createMessage('Video', 'Replica hashtags en ventanas de alta exposicion.', 'Hace 22 s'),
        this.createMessage('NLP', 'Frases de captacion reiteradas dentro del cluster.', 'Hace 39 s')
      ]),
      this.createNode('north-h1', 'north', 'hub', 0.2, 0.15, 'Mariana Solis', '@mar.sol', 'Instagram', 182, 'Carga incremental', 82, 72, 63, 'Hub con comentarios espejo y reacciones recurrentes.', [
        this.createMessage('Story', 'Relacion moderada con respuestas espejo.', 'Hace 19 s'),
        this.createMessage('Comentario', 'Replica frases del recruiter central.', 'Hace 44 s')
      ]),
      this.createNode('north-h2', 'north', 'hub', 0.1, 0.28, 'Diego Cortes', '@d.cortes', 'Facebook', 149, 'OCR + scraping', 74, 67, 54, 'Nodo de amplificacion por compartidos y etiquetas.', [
        this.createMessage('Post', 'Distribuye enlaces hacia perfiles nuevos.', 'Hace 27 s')
      ]),
      this.createNode('north-b1', 'north', 'bridge', 0.27, 0.26, 'Renata Leon', '@renata.leon', 'X', 97, 'Carga batch', 64, 43, 29, 'Puente entre el cluster norte y centro.', [
        this.createMessage('Reply', 'Coincidencia parcial en hilos de observacion.', 'Hace 32 s')
      ]),
      this.createNode('north-o1', 'north', 'observer', 0.06, 0.18, 'Leonardo Pina', '@leo.pina', 'TikTok', 81, 'Carga incremental', 58, 35, 18, 'Cuenta observadora con interaccion debil pero frecuente.', [
        this.createMessage('View', 'Repite visualizaciones sobre contenido del recruiter.', 'Hace 35 s')
      ]),
      this.createNode('north-t1', 'north', 'target', 0.19, 0.36, 'Karla Mendez', '@karla.mdz', 'Instagram', 54, 'Scraping continuo', 77, 58, 45, 'Target con incremento progresivo en comentarios cruzados.', [
        this.createMessage('Comentario', 'Aumento de interacciones desde el hub secundario.', 'Hace 26 s')
      ]),
      this.createNode('north-t2', 'north', 'target', 0.03, 0.3, 'Joel Murillo', '@joel.mur', 'Facebook', 48, 'Carga batch', 62, 39, 22, 'Perfil lateral con contacto parcial.', [
        this.createMessage('Post', 'Relacion baja por compartidos aislados.', 'Hace 41 s')
      ]),

      this.createNode('center-r0', 'center', 'recruiter', 0.44, 0.32, 'Valeria Cruz', '@valcrz.ops', 'TikTok', 221, 'Carga incremental', 92, 84, 81, 'Recruiter central con enlaces cruzados a tres subredes.', [
        this.createMessage('Comentario', 'Recibe trafico sincronizado de hubs y targets.', 'Hace 11 s'),
        this.createMessage('Video', 'Dispara respuestas en cascada.', 'Hace 25 s'),
        this.createMessage('NLP', 'Convergencia semantica elevada en mensajes de riesgo.', 'Hace 48 s')
      ]),
      this.createNode('center-h1', 'center', 'hub', 0.38, 0.25, 'Sofia Rivas', '@sof.radar', 'Facebook', 194, 'Scraping continuo', 95, 87, 76, 'Hub de comentarios, reacciones y posts derivados.', [
        this.createMessage('Post', 'Agrupa enlaces reutilizados por nodos conectados.', 'Hace 17 s')
      ]),
      this.createNode('center-h2', 'center', 'hub', 0.54, 0.23, 'Camila Ortega', '@cami.route', 'TikTok', 172, 'Carga incremental', 84, 73, 58, 'Hub espejo con duetos y menciones encadenadas.', [
        this.createMessage('Video', 'Propaga el mismo audio hacia nodos secundarios.', 'Hace 29 s')
      ]),
      this.createNode('center-b1', 'center', 'bridge', 0.36, 0.42, 'Ana Leal', '@ana.bridge', 'Instagram', 88, 'OCR + scraping', 66, 44, 27, 'Conecta el centro con rutas laterales.', [
        this.createMessage('DM', 'Cruce parcial con clusters sur y norte.', 'Hace 37 s')
      ]),
      this.createNode('center-b2', 'center', 'bridge', 0.56, 0.43, 'Ivan Soria', '@ivn.soria', 'Instagram', 91, 'Carga incremental', 71, 51, 34, 'Bridge con tags recurrentes y actividad media.', [
        this.createMessage('Story', 'Relacion baja-media con menciones cruzadas.', 'Hace 24 s')
      ]),
      this.createNode('center-t1', 'center', 'target', 0.44, 0.53, 'Mateo Solis', '@m.solis.feed', 'X', 109, 'Carga batch', 74, 62, 52, 'Target con respuestas en ventanas cortas.', [
        this.createMessage('Reply', 'Sube la cadencia de respuesta tras cada publicacion central.', 'Hace 14 s')
      ]),
      this.createNode('center-t2', 'center', 'target', 0.61, 0.36, 'Erik Ponce', '@erik.snap', 'Instagram', 67, 'OCR + transcripcion', 58, 41, 24, 'Nodo periferico con visualizaciones repetidas.', [
        this.createMessage('Story', 'Coincidencia ligera en visualizaciones y likes.', 'Hace 31 s')
      ]),
      this.createNode('center-o1', 'center', 'observer', 0.31, 0.34, 'Paola Meza', '@pao.edge', 'Facebook', 58, 'Carga batch', 55, 36, 16, 'Observador lateral con comentarios de baja profundidad.', [
        this.createMessage('Post', 'Mantiene observacion sobre perfiles de riesgo medio.', 'Hace 46 s')
      ]),

      this.createNode('east-r0', 'east', 'recruiter', 0.75, 0.24, 'Lucia Bernal', '@lu.bernal', 'Facebook', 243, 'Scraping continuo', 94, 89, 79, 'Recruiter del cluster este con densidad alta en compartidos.', [
        this.createMessage('Post', 'Sostiene difusion de enlaces hacia targets del este.', 'Hace 8 s'),
        this.createMessage('Comentario', 'Replica frases gatillo en nodos con alto engagement.', 'Hace 19 s'),
        this.createMessage('NLP', 'La persistencia semantica rebasa el umbral.', 'Hace 42 s')
      ]),
      this.createNode('east-h1', 'east', 'hub', 0.68, 0.16, 'Renata Quintero', '@renaqt', 'Facebook', 168, 'OCR + scraping', 92, 85, 74, 'Hub con republicaciones y reforzamiento cruzado.', [
        this.createMessage('Post', 'Activa cadenas de compartidos.', 'Hace 21 s')
      ]),
      this.createNode('east-h2', 'east', 'hub', 0.85, 0.18, 'Marco Ibarra', '@m.ibarra', 'X', 187, 'Carga batch', 97, 93, 92, 'Hub critico con respuestas automatizadas.', [
        this.createMessage('Reply', 'Relacion total con el recruiter del este.', 'Hace 6 s'),
        this.createMessage('Alerta', 'Se observan contactos insistentes con cuentas nuevas.', 'Hace 23 s')
      ]),
      this.createNode('east-b1', 'east', 'bridge', 0.72, 0.37, 'Gael Trujillo', '@gael.flow', 'X', 98, 'Carga incremental', 68, 52, 33, 'Bridge entre el este y los hubs del sur.', [
        this.createMessage('Reply', 'Conecta conversaciones entre subredes activas.', 'Hace 27 s')
      ]),
      this.createNode('east-t1', 'east', 'target', 0.88, 0.3, 'Nadia Ruiz', '@nadiarx', 'TikTok', 142, 'Scraping continuo', 87, 81, 76, 'Target de alto riesgo con respuestas encadenadas.', [
        this.createMessage('Video', 'Relacion alta por repeticion de audio y hashtags.', 'Hace 15 s')
      ]),
      this.createNode('east-t2', 'east', 'target', 0.81, 0.42, 'Diego Mena', '@dm.sync', 'Instagram', 72, 'Normalizacion OCR', 69, 46, 28, 'Target con actividad baja-media y cruces intermitentes.', [
        this.createMessage('Story', 'Interactua en franjas sincronizadas con el cluster.', 'Hace 38 s')
      ]),
      this.createNode('east-o1', 'east', 'observer', 0.66, 0.28, 'Joel Murillo', '@joel.mur', 'Facebook', 51, 'Carga batch', 57, 37, 15, 'Observador con republicaciones ligeras.', [
        this.createMessage('Post', 'Acompaña la difusion sin ser nodo principal.', 'Hace 43 s')
      ]),

      this.createNode('south-r0', 'south', 'recruiter', 0.62, 0.68, 'Axel Fuentes', '@axel.fts', 'Instagram', 206, 'Carga incremental', 89, 83, 72, 'Recruiter del cluster sur con crecimiento acelerado.', [
        this.createMessage('Comentario', 'Coordina actividad de hubs inferiores.', 'Hace 13 s'),
        this.createMessage('DM', 'Escala contacto privado despues de picos de interaccion.', 'Hace 34 s')
      ]),
      this.createNode('south-h1', 'south', 'hub', 0.54, 0.8, 'Daniel Vite', '@dv.left', 'TikTok', 128, 'Scraping continuo', 83, 74, 57, 'Hub del sur con menciones cruzadas y trafico nocturno.', [
        this.createMessage('Comentario', 'Relacion moderada por comentarios espejo y replies.', 'Hace 18 s')
      ]),
      this.createNode('south-h2', 'south', 'hub', 0.72, 0.8, 'Yara Beltran', '@yarab', 'Facebook', 113, 'Carga incremental', 77, 63, 48, 'Hub secundario con republicacion sostenida.', [
        this.createMessage('Story', 'Redistribuye vistas y etiquetas hacia targets del sur.', 'Hace 33 s')
      ]),
      this.createNode('south-b1', 'south', 'bridge', 0.49, 0.67, 'Leonardo Pina', '@leo.pina', 'TikTok', 78, 'Carga batch', 61, 44, 24, 'Bridge hacia los clusters centro y norte.', [
        this.createMessage('View', 'Conecta ventanas de observacion entre recruiters.', 'Hace 28 s')
      ]),
      this.createNode('south-t1', 'south', 'target', 0.61, 0.91, 'Mateo Rocha', '@m.rocha', 'X', 71, 'OCR + scraping', 64, 49, 37, 'Target con actividad media y retweets recurrentes.', [
        this.createMessage('Reply', 'Responde a nodos superiores con frecuencia sostenida.', 'Hace 17 s')
      ]),
      this.createNode('south-t2', 'south', 'target', 0.78, 0.9, 'Karla Mendez', '@karla.mdz', 'Instagram', 86, 'Scraping continuo', 79, 68, 61, 'Target con alta correlacion de compartidos y comentarios.', [
        this.createMessage('Post', 'Relacion moderada-alta por publicaciones en espejo.', 'Hace 22 s')
      ]),
      this.createNode('south-o1', 'south', 'observer', 0.68, 0.58, 'Paula Rios', '@paula.r', 'Instagram', 47, 'Carga batch', 53, 31, 14, 'Observador con actividad leve sobre el recruiter del sur.', [
        this.createMessage('Story', 'Mantiene observacion pasiva y reacciones ocasionales.', 'Hace 40 s')
      ])
    ];

    const links: ThreatLink[] = [
      ...this.buildClusterLinks(['north-r0', 'north-h1', 'north-h2', 'north-b1', 'north-o1', 'north-t1', 'north-t2']),
      ...this.buildClusterLinks(['center-r0', 'center-h1', 'center-h2', 'center-b1', 'center-b2', 'center-t1', 'center-t2', 'center-o1']),
      ...this.buildClusterLinks(['east-r0', 'east-h1', 'east-h2', 'east-b1', 'east-t1', 'east-t2', 'east-o1']),
      ...this.buildClusterLinks(['south-r0', 'south-h1', 'south-h2', 'south-b1', 'south-t1', 'south-t2', 'south-o1']),
      { source: 'north-r0', target: 'center-r0', strength: 0.62 },
      { source: 'center-r0', target: 'east-r0', strength: 0.57 },
      { source: 'center-r0', target: 'south-r0', strength: 0.52 },
      { source: 'north-b1', target: 'center-b1', strength: 0.34 },
      { source: 'center-b2', target: 'south-b1', strength: 0.29 },
      { source: 'east-b1', target: 'south-h2', strength: 0.47 },
      { source: 'north-h1', target: 'center-h1', strength: 0.44 },
      { source: 'east-h2', target: 'center-h2', strength: 0.68 },
      { source: 'south-h1', target: 'center-t1', strength: 0.41 }
    ];

    const centrality = new Map<string, number>();
    for (const node of rawNodes) {
      centrality.set(node.id, 0);
    }
    for (const link of links) {
      centrality.set(link.source, (centrality.get(link.source) ?? 0) + 1);
      centrality.set(link.target, (centrality.get(link.target) ?? 0) + 1);
    }

    return {
      nodes: rawNodes.map((node) => ({
        ...node,
        centrality: centrality.get(node.id) ?? 0
      })),
      links
    };
  }

  private buildClusterLinks(ids: string[]): ThreatLink[] {
    const recruiter = ids[0];
    const links: ThreatLink[] = [];

    for (let index = 1; index < ids.length; index += 1) {
      const target = ids[index];
      const strength = index < 3 ? 0.76 : index < 5 ? 0.48 : 0.3 + index * 0.04;
      links.push({ source: recruiter, target, strength: Math.min(strength, 0.92) });
    }

    for (let index = 1; index < ids.length - 1; index += 1) {
      links.push({
        source: ids[index],
        target: ids[index + 1],
        strength: 0.22 + (index % 5) * 0.11
      });
    }

    if (ids.length > 5) {
      links.push({ source: ids[1], target: ids[4], strength: 0.55 });
      links.push({ source: ids[2], target: ids[5], strength: 0.67 });
    }

    return links;
  }

  private createNode(
    id: string,
    clusterId: string,
    role: NodeRole,
    anchorX: number,
    anchorY: number,
    userName: string,
    handle: string,
    platform: string,
    publications: number,
    loadMethod: string,
    loadProgress: number,
    scrapingValue: number,
    relationScore: number,
    summary: string,
    messages: ThreatMessage[]
  ): RawNode {
    return {
      id,
      clusterId,
      role,
      radius: role === 'recruiter' ? 18 : role === 'hub' ? 14 : role === 'bridge' ? 11 : role === 'target' ? 10 : 8,
      anchorX,
      anchorY,
      userName,
      handle,
      platform,
      publications,
      loadMethod,
      loadProgress,
      scrapingValue,
      relationScore,
      summary,
      messages
    };
  }

  private createMessage(channel: string, text: string, timestamp: string): ThreatMessage {
    return { channel, text, timestamp };
  }
}
