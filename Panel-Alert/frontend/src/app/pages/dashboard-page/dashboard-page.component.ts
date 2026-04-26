import {
  AfterViewInit,
  Component,
  ElementRef,
  computed,
  inject,
  signal
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { animate, stagger } from 'animejs';
import { AuthService } from '../../services/auth.service';

type PanelSection = 'alerts' | 'blocks' | 'devices';
type AlertSeverity = 'weak' | 'low' | 'moderate' | 'critical';
type AlertStatus = 'open' | 'authorized' | 'blocked';

type AlertItem = {
  id: string;
  userName: string;
  platform: string;
  rating: number;
  status: AlertStatus;
};

type BlockItem = {
  id: string;
  contentLabel: string;
  platform: string;
  reason: string;
  linkedChild: string;
  blockedAt: string;
  status: string;
};

type DeviceItem = {
  id: string;
  label: string;
  childName: string;
  activity: string;
  lastSeen: string;
  status: 'watch' | 'linked';
};

type ToastKind = 'info' | 'success' | 'danger';

type ToastItem = {
  id: number;
  title: string;
  label: string;
  description: string;
  kind: ToastKind;
};

@Component({
  selector: 'app-dashboard-page',
  imports: [CommonModule],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.css'
})
export class DashboardPageComponent implements AfterViewInit {
  private readonly elementRef = inject(ElementRef<HTMLElement>);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private toastCounter = 1;

  protected readonly session = this.authService.session;
  protected readonly activeSection = signal<PanelSection>('alerts');
  protected readonly alerts = signal<AlertItem[]>([
    {
      id: 'alert-01',
      userName: 'marlon.vega',
      platform: 'TikTok',
      rating: 94,
      status: 'open'
    },
    {
      id: 'alert-02',
      userName: 'lucia.moreno',
      platform: 'Instagram',
      rating: 71,
      status: 'open'
    },
    {
      id: 'alert-03',
      userName: 'joel.ramos',
      platform: 'Facebook',
      rating: 39,
      status: 'authorized'
    }
  ]);
  protected readonly blocks = signal<BlockItem[]>([
    {
      id: 'block-01',
      contentLabel: 'Video: DM invite with coded language',
      platform: 'TikTok',
      reason:
        'Contenido clasificado como no apto para ninos por invitacion con lenguaje de enganche.',
      linkedChild: 'Profile: Sofia / Age filter 11-13',
      blockedAt: 'Hoy · 09:12',
      status: 'Restringido'
    },
    {
      id: 'block-02',
      contentLabel: 'Account: @night.route',
      platform: 'Instagram',
      reason:
        'Cuenta restringida por exposicion repetida a publicaciones no seguras para menores.',
      linkedChild: 'Profile: Mateo / Age filter 12-14',
      blockedAt: 'Hoy · 08:47',
      status: 'Restringido'
    }
  ]);
  protected readonly devices = signal<DeviceItem[]>([
    {
      id: 'device-01',
      label: 'iPhone 14 Pro',
      childName: 'Sofia Gomez',
      activity: 'Dispositivo principal vinculado por el tutor para supervision diaria.',
      lastSeen: 'Visto hace 18 s',
      status: 'watch'
    },
    {
      id: 'device-02',
      label: 'Galaxy S23',
      childName: 'Mateo Ruiz',
      activity: 'Dispositivo vinculado al perfil infantil para seguimiento de actividad.',
      lastSeen: 'Visto hace 2 min',
      status: 'linked'
    },
    {
      id: 'device-03',
      label: 'Android Tablet',
      childName: 'Valeria Torres',
      activity: 'Tablet vinculada al perfil infantil para control de uso y monitoreo.',
      lastSeen: 'Visto hace 14 min',
      status: 'linked'
    }
  ]);
  protected readonly toasts = signal<ToastItem[]>([
    {
      id: 1,
      title: 'Panel activo',
      label: 'INFO',
      description: 'HarborWatch conectado al flujo de supervision parental.',
      kind: 'info'
    }
  ]);

  protected readonly actionableAlerts = computed(() =>
    this.alerts().filter((alert) => this.isActionableRating(alert.rating))
  );
  protected readonly openAlertsCount = computed(
    () => this.actionableAlerts().filter((alert) => alert.status === 'open').length
  );
  protected readonly activeBlocksCount = computed(() => this.blocks().length);
  protected readonly linkedDevicesCount = computed(() => this.devices().length);
  protected readonly sectionTitle = computed(() => {
    if (this.activeSection() === 'blocks') return 'Contenido y cuentas restringidas';
    if (this.activeSection() === 'devices') return 'Dispositivos vinculados';
    return 'Cola de alertas';
  });
  protected readonly sectionSubtitle = computed(() => {
    if (this.activeSection() === 'blocks') {
      return 'Revisa el contenido y las cuentas bloqueadas por no ser aptas para ninos.';
    }
    if (this.activeSection() === 'devices') {
      return 'Consulta los dispositivos vinculados de tus hijos y activa monitoreo cuando lo necesites.';
    }
    return 'Revisa solo alertas naranja y roja para decidir si deben bloquearse o autorizarse.';
  });

  ngAfterViewInit(): void {
    const host = this.elementRef.nativeElement;

    animate(host.querySelectorAll('.panel-surface, .toast-card'), {
      opacity: [0, 1],
      y: [20, 0],
      duration: 760,
      delay: stagger(70),
      ease: 'outExpo'
    });
  }

  protected setSection(section: PanelSection): void {
    this.activeSection.set(section);
  }

  protected signOut(): void {
    this.authService.signOut();
    void this.router.navigate(['/login']);
  }

  protected severityLabel(severity: AlertSeverity): string {
    if (severity === 'critical') return 'Riesgo alto';
    if (severity === 'moderate') return 'Moderado';
    if (severity === 'low') return 'Bajo';
    return 'Debil';
  }

  protected severityFromRating(rating: number): AlertSeverity {
    if (rating <= 20) return 'weak';
    if (rating <= 45) return 'low';
    if (rating <= 75) return 'moderate';
    return 'critical';
  }

  protected severityLabelFromRating(rating: number): string {
    return this.severityLabel(this.severityFromRating(rating));
  }

  protected isActionableRating(rating: number): boolean {
    const severity = this.severityFromRating(rating);
    return severity === 'moderate' || severity === 'critical';
  }

  protected deviceStatusLabel(status: DeviceItem['status']): string {
    if (status === 'watch') return 'Monitoreando';
    return 'Vinculado';
  }

  protected usernameLabel(userName: string): string {
    return userName.startsWith('@') ? userName : `@${userName}`;
  }

  protected blockAlert(alertId: string): void {
    const targetAlert = this.alerts().find((alert) => alert.id === alertId);
    if (!targetAlert) return;

    this.alerts.update((alerts) =>
      alerts.map((alert) =>
        alert.id === alertId ? { ...alert, status: 'blocked' } : alert
      )
    );

    this.blocks.update((blocks) => [
      {
        id: `block-${alertId}`,
        contentLabel: `Cuenta: ${this.usernameLabel(targetAlert.userName)}`,
        platform: targetAlert.platform,
        reason: `Cuenta restringida por alerta automatica con user rating de ${targetAlert.rating}% y nivel de riesgo ${this.severityLabelFromRating(targetAlert.rating).toLowerCase()}.`,
        linkedChild: 'Perfil infantil en revision',
        blockedAt: 'Ahora',
        status: 'Restringido'
      },
      ...blocks
    ]);

    this.pushToast(
      'Usuario bloqueado',
      'DANGER',
      `${this.usernameLabel(targetAlert.userName)} fue enviado al registro de cuentas restringidas.`,
      'danger'
    );
  }

  protected authorizeAlert(alertId: string): void {
    const targetAlert = this.alerts().find((alert) => alert.id === alertId);
    if (!targetAlert) return;

    this.alerts.update((alerts) =>
      alerts.map((alert) =>
        alert.id === alertId ? { ...alert, status: 'authorized' } : alert
      )
    );

    this.pushToast(
      'Alerta autorizada',
      'SUCCESS',
      `${this.usernameLabel(targetAlert.userName)} fue autorizado por el operador.`,
      'success'
    );
  }

  protected flagDevice(deviceId: string): void {
    const targetDevice = this.devices().find((device) => device.id === deviceId);
    if (!targetDevice) return;

    this.devices.update((devices) =>
      devices.map((device) =>
        device.id === deviceId ? { ...device, status: 'watch' } : device
      )
    );

    this.pushToast(
      'Dispositivo en monitoreo',
      'INFO',
      `${targetDevice.label} quedo con monitoreo activo para el perfil infantil.`,
      'info'
    );
  }

  private pushToast(
    title: string,
    label: string,
    description: string,
    kind: ToastKind
  ): void {
    const nextId = ++this.toastCounter;
    const nextToast: ToastItem = { id: nextId, title, label, description, kind };

    this.toasts.update((toasts) => [...toasts, nextToast]);

    setTimeout(() => {
      this.toasts.update((toasts) => toasts.filter((toast) => toast.id !== nextId));
    }, 4200);
  }
}
