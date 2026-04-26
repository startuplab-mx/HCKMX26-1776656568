import {
  AfterViewInit,
  Component,
  ElementRef,
  inject
} from '@angular/core';
import { Router } from '@angular/router';
import { animate } from 'animejs';
import { ThreatNetworkComponent } from '../../components/threat-network/threat-network.component';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard-page',
  imports: [ThreatNetworkComponent],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.css'
})
export class DashboardPageComponent implements AfterViewInit {
  private readonly elementRef = inject(ElementRef<HTMLElement>);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  ngAfterViewInit(): void {
    const host = this.elementRef.nativeElement;

    animate(host.querySelector('.dashboard-shell'), {
      opacity: [0, 1],
      y: [18, 0],
      duration: 820,
      ease: 'outExpo'
    });
  }

  protected signOut(): void {
    this.authService.signOut();
    void this.router.navigate(['/login']);
  }
}
