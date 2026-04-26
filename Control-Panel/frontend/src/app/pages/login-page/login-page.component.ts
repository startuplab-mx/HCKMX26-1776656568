import {
  AfterViewInit,
  Component,
  ElementRef,
  inject
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { animate, stagger } from 'animejs';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login-page',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.css'
})
export class LoginPageComponent implements AfterViewInit {
  private readonly formBuilder = inject(FormBuilder);
  private readonly router = inject(Router);
  private readonly elementRef = inject(ElementRef<HTMLElement>);
  private readonly authService = inject(AuthService);

  protected readonly loginForm = this.formBuilder.nonNullable.group({
    operatorId: ['', [Validators.required, Validators.minLength(4)]],
    accessKey: ['', [Validators.required, Validators.minLength(8)]]
  });
  protected invalidCredentials = false;

  ngAfterViewInit(): void {
    const host = this.elementRef.nativeElement;

    animate(host.querySelectorAll('.panel-surface'), {
      opacity: [0, 1],
      y: [28, 0],
      duration: 900,
      delay: stagger(120),
      ease: 'outExpo'
    });

    animate(host.querySelectorAll('.message-stream span'), {
      opacity: [0, 1],
      x: [-18, 0],
      duration: 880,
      delay: stagger(140, { start: 220 }),
      ease: 'outExpo'
    });
  }

  protected signIn(): void {
    if (this.loginForm.invalid) {
      this.invalidCredentials = false;
      this.loginForm.markAllAsTouched();
      return;
    }

    const { operatorId, accessKey } = this.loginForm.getRawValue();
    this.invalidCredentials = !this.authService.signIn(operatorId, accessKey);

    if (this.invalidCredentials) {
      return;
    }

    void this.router.navigate(['/dashboard']);
  }
}
