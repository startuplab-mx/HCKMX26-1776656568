import {
  AfterViewInit,
  Component,
  ElementRef,
  computed,
  inject
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { animate, stagger } from 'animejs';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-home-page',
  imports: [RouterLink],
  templateUrl: './home-page.component.html',
  styleUrl: './home-page.component.css'
})
export class HomePageComponent implements AfterViewInit {
  private readonly elementRef = inject(ElementRef<HTMLElement>);
  private readonly authService = inject(AuthService);

  protected readonly session = this.authService.session;
  protected readonly isAuthenticated = computed(() => this.session() !== null);
  protected readonly trustMetrics = [
    { value: '24/7', label: 'revision continua' },
    { value: '92%', label: 'lectura priorizada' },
    { value: '4 capas', label: 'contexto relacional' }
  ] as const;
  protected readonly activeAlerts = [
    'Cluster norte',
    'Difusion coordinada',
    'Escalamiento privado'
  ] as const;
  protected readonly whoWeAreCards = [
    {
      icon: '01',
      title: 'Analisis con contexto',
      description: 'Entender relaciones, intensidad y comportamiento dentro de una misma lectura.'
    },
    {
      icon: '02',
      title: 'Interfaz institucional',
      description: 'Una experiencia visual mas seria, limpia y adecuada para presentacion.'
    },
    {
      icon: '03',
      title: 'Diseno orientado a decision',
      description: 'Cada bloque esta pensado para facilitar lectura sin saturacion.'
    }
  ] as const;
  protected readonly capabilities = [
    {
      title: 'Mapeo de relaciones',
      description: 'Organiza interacciones entre cuentas y jerarquiza nodos relevantes.'
    },
    {
      title: 'Priorizacion de riesgo',
      description: 'Ordena las senales para identificar primero lo que exige atencion.'
    },
    {
      title: 'Concentracion de evidencia',
      description: 'Resume actividad y contexto dentro de una sola revision.'
    }
  ] as const;
  protected readonly differentiators = [
    {
      title: 'Narrativa profesional',
      description: 'La landing comunica la propuesta sin sentirse experimental.'
    },
    {
      title: 'Claridad antes que ruido',
      description: 'Los mensajes son breves y la jerarquia visual es mas limpia.'
    },
    {
      title: 'Continuidad de flujo',
      description: 'La entrada hacia login y dashboard se siente natural y directa.'
    }
  ] as const;

  ngAfterViewInit(): void {
    const host = this.elementRef.nativeElement;

    animate(host.querySelectorAll('.reveal-panel'), {
      opacity: [0, 1],
      y: [30, 0],
      duration: 900,
      delay: stagger(110),
      ease: 'outExpo'
    });

    animate(host.querySelectorAll('.floating-node'), {
      opacity: [0, 1],
      x: [-18, 0],
      duration: 780,
      delay: stagger(120, { start: 260 }),
      ease: 'outExpo'
    });
  }
}
