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
