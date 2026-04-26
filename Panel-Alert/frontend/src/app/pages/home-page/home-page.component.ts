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
    { value: '24/7', label: 'live alert visibility' },
    { value: '3 views', label: 'alerts, blocks, devices' },
    { value: 'real-time', label: 'toast event feedback' }
  ] as const;
  protected readonly activeAlerts = [
    'High-risk user detected',
    'Block applied successfully',
    'New device under review'
  ] as const;
  protected readonly whoWeAreCards = [
    {
      icon: '01',
      title: 'Operational review',
      description: 'A focused interface for operators reviewing sensitive moderation cases.'
    },
    {
      icon: '02',
      title: 'Professional console',
      description: 'A cleaner enterprise-style presentation for demos, juries and stakeholders.'
    },
    {
      icon: '03',
      title: 'Fast decision flow',
      description: 'Built to move from alert review into block or authorization with less friction.'
    }
  ] as const;
  protected readonly capabilities = [
    {
      title: 'Alert management',
      description: 'Review users flagged as unsafe and understand why they were escalated.'
    },
    {
      title: 'Block workflow',
      description: 'Apply restrictions to critical users directly from the operator dashboard.'
    },
    {
      title: 'Device visibility',
      description: 'Track devices linked to suspicious activity and keep them under watch.'
    }
  ] as const;
  protected readonly differentiators = [
    {
      title: 'Clear hierarchy',
      description: 'The landing explains the product without looking overloaded or experimental.'
    },
    {
      title: 'Better moderation flow',
      description: 'Operators move between alerts, blocks and devices from a single workspace.'
    },
    {
      title: 'Toast event system',
      description: 'Status messages stack from the bottom-right and disappear automatically.'
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
