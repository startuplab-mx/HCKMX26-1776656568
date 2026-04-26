import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  inject
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { animate, stagger } from 'animejs';
import { AuthService } from '../../services/auth.service';

type GoogleCredentialResponse = {
  credential: string;
  select_by: string;
};

type GoogleJwtPayload = {
  sub?: string;
  name?: string;
  email?: string;
};

type GoogleButtonOptions = {
  theme: 'outline' | 'filled_blue' | 'filled_black';
  size: 'large' | 'medium' | 'small';
  text: 'signin_with' | 'continue_with' | 'signup_with';
  shape: 'rectangular' | 'pill' | 'circle' | 'square';
  width?: string;
  logo_alignment?: 'left' | 'center';
};

type GoogleIdConfiguration = {
  client_id: string;
  callback: (response: GoogleCredentialResponse) => void;
  auto_select?: boolean;
  cancel_on_tap_outside?: boolean;
  ux_mode?: 'popup' | 'redirect';
};

type GoogleAccounts = {
  id: {
    initialize: (config: GoogleIdConfiguration) => void;
    renderButton: (element: HTMLElement, options: GoogleButtonOptions) => void;
  };
};

declare global {
  interface Window {
    google?: {
      accounts: GoogleAccounts;
    };
  }
}

@Component({
  selector: 'app-register-page',
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './register-page.component.html',
  styleUrl: './register-page.component.css'
})
export class RegisterPageComponent implements AfterViewInit, OnDestroy {
  private static readonly googleClientId =
    '3504800246-bg1c9bhujuhi2bkmktr1da5n4eofap80.apps.googleusercontent.com';
  private static readonly maxGoogleInitAttempts = 20;
  private readonly formBuilder = inject(FormBuilder);
  private readonly router = inject(Router);
  private readonly elementRef = inject(ElementRef<HTMLElement>);
  private readonly authService = inject(AuthService);
  private googleRenderAttempt: ReturnType<typeof setTimeout> | null = null;
  private googleInitAttempts = 0;

  protected readonly registerForm = this.formBuilder.nonNullable.group({
    fullName: ['', [Validators.required, Validators.minLength(4)]],
    email: ['', [Validators.required, Validators.email]],
    operatorId: ['', [Validators.required, Validators.minLength(4)]],
    accessKey: ['', [Validators.required, Validators.minLength(8)]]
  });
  protected duplicateAccount = false;
  protected googleAuthError = '';
  protected googleButtonReady = false;

  ngAfterViewInit(): void {
    const host = this.elementRef.nativeElement;

    animate(host.querySelectorAll('.panel-surface'), {
      opacity: [0, 1],
      y: [28, 0],
      duration: 900,
      delay: stagger(120),
      ease: 'outExpo'
    });

    this.initializeGoogleButton();
  }

  ngOnDestroy(): void {
    if (this.googleRenderAttempt) {
      clearTimeout(this.googleRenderAttempt);
    }
  }

  protected register(): void {
    if (this.registerForm.invalid) {
      this.duplicateAccount = false;
      this.registerForm.markAllAsTouched();
      return;
    }

    const { fullName, email, operatorId, accessKey } = this.registerForm.getRawValue();
    const registered = this.authService.registerOperator(fullName, email, operatorId, accessKey);

    if (!registered) {
      this.duplicateAccount = true;
      return;
    }

    void this.router.navigate(['/login']);
  }

  private initializeGoogleButton(): void {
    const host = this.elementRef.nativeElement as HTMLElement;
    const buttonContainer = host.querySelector('#google-signup-button') as HTMLElement | null;

    if (!buttonContainer) {
      this.googleAuthError = 'No se encontro el contenedor del acceso con Google.';
      return;
    }

    const googleAccounts = window.google?.accounts;
    if (!googleAccounts) {
      this.googleInitAttempts += 1;
      if (this.googleInitAttempts >= RegisterPageComponent.maxGoogleInitAttempts) {
        this.googleAuthError =
          'Google secure access is not available right now. Check your client configuration and allowed origins.';
        return;
      }

      this.googleRenderAttempt = setTimeout(() => this.initializeGoogleButton(), 250);
      return;
    }

    buttonContainer.innerHTML = '';
    googleAccounts.id.initialize({
      client_id: RegisterPageComponent.googleClientId,
      callback: (response) => this.handleGoogleCredential(response),
      auto_select: false,
      cancel_on_tap_outside: true,
      ux_mode: 'popup'
    });
    googleAccounts.id.renderButton(buttonContainer, {
      theme: 'outline',
      size: 'large',
      text: 'signup_with',
      shape: 'pill',
      width: '320',
      logo_alignment: 'left'
    });

    this.googleButtonReady = true;
    this.googleAuthError = '';
    this.googleInitAttempts = 0;
    this.googleRenderAttempt = null;
  }

  private handleGoogleCredential(response: GoogleCredentialResponse): void {
    try {
      const payload = this.decodeGoogleJwt(response.credential);
      const googleId = payload.sub?.trim();
      const email = payload.email?.trim().toLowerCase();

      if (!googleId || !email) {
        this.googleAuthError = 'Google no devolvio una identidad valida para iniciar sesion.';
        return;
      }

      this.authService.signInWithGoogle({
        fullName: payload.name?.trim() || email,
        email,
        googleId
      });
      this.googleAuthError = '';
      void this.router.navigate(['/dashboard']);
    } catch {
      this.googleAuthError = 'No fue posible procesar la credencial de Google.';
    }
  }

  private decodeGoogleJwt(token: string): GoogleJwtPayload {
    const [, payloadSegment] = token.split('.');

    if (!payloadSegment) {
      throw new Error('Invalid JWT payload');
    }

    const normalizedPayload = payloadSegment
      .replace(/-/g, '+')
      .replace(/_/g, '/')
      .padEnd(Math.ceil(payloadSegment.length / 4) * 4, '=');
    const decodedPayload = atob(normalizedPayload);
    const bytes = Uint8Array.from(decodedPayload, (char) => char.charCodeAt(0));
    const jsonPayload = new TextDecoder().decode(bytes);

    return JSON.parse(jsonPayload) as GoogleJwtPayload;
  }
}
