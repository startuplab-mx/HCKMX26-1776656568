import { Injectable, signal } from '@angular/core';

type StoredSession = {
  operatorId: string;
  fullName: string;
};

type GoogleIdentityProfile = {
  fullName: string;
  email: string;
  googleId: string;
};

type RegisteredOperator = {
  fullName: string;
  email: string;
  operatorId: string;
  accessKey: string;
};

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly sessionStorageKey = 'panel.alert.session';
  private readonly accountsStorageKey = 'panel.alert.accounts';
  private readonly demoCredentials = {
    fullName: 'Demo Operator',
    operatorId: 'OPS-2048',
    accessKey: 'guardian404'
  } as const;
  private readonly sessionState = signal<StoredSession | null>(this.readStoredSession());

  readonly session = this.sessionState.asReadonly();

  isAuthenticated(): boolean {
    return this.sessionState() !== null;
  }

  registerOperator(
    fullName: string,
    email: string,
    operatorId: string,
    accessKey: string
  ): boolean {
    const normalizedFullName = fullName.trim();
    const normalizedEmail = email.trim().toLowerCase();
    const normalizedOperatorId = operatorId.trim().toUpperCase();
    const normalizedAccessKey = accessKey.trim();

    const accounts = this.readStoredAccounts();
    const alreadyExists = accounts.some(
      (account) =>
        account.operatorId === normalizedOperatorId || account.email === normalizedEmail
    );

    if (alreadyExists) {
      return false;
    }

    accounts.push({
      fullName: normalizedFullName,
      email: normalizedEmail,
      operatorId: normalizedOperatorId,
      accessKey: normalizedAccessKey
    });

    this.persistAccounts(accounts);
    return true;
  }

  signIn(operatorId: string, accessKey: string): boolean {
    const normalizedOperatorId = operatorId.trim().toUpperCase();
    const normalizedAccessKey = accessKey.trim();
    const demoMatch =
      normalizedOperatorId === this.demoCredentials.operatorId &&
      normalizedAccessKey === this.demoCredentials.accessKey;
    const registeredMatch = this.readStoredAccounts().find(
      (account) =>
        account.operatorId === normalizedOperatorId &&
        account.accessKey === normalizedAccessKey
    );

    if (!demoMatch && !registeredMatch) {
      return false;
    }

    const session = {
      operatorId: normalizedOperatorId,
      fullName: registeredMatch?.fullName ?? this.demoCredentials.fullName
    };
    this.sessionState.set(session);
    this.persistSession(session);
    return true;
  }

  signInWithGoogle(profile: GoogleIdentityProfile): void {
    const normalizedFullName = profile.fullName.trim();
    const normalizedEmail = profile.email.trim().toLowerCase();
    const normalizedGoogleId = profile.googleId.trim();
    const session = {
      operatorId: this.createGoogleOperatorId(normalizedGoogleId, normalizedEmail),
      fullName: normalizedFullName || normalizedEmail || 'Google Operator'
    };

    this.sessionState.set(session);
    this.persistSession(session);
  }

  signOut(): void {
    this.sessionState.set(null);
    this.storage?.removeItem(this.sessionStorageKey);
  }

  private get storage(): Storage | null {
    if (typeof globalThis === 'undefined' || !('localStorage' in globalThis)) {
      return null;
    }

    return globalThis.localStorage;
  }

  private readStoredSession(): StoredSession | null {
    const rawSession = this.storage?.getItem(this.sessionStorageKey);

    if (!rawSession) {
      return null;
    }

    try {
      const parsedSession = JSON.parse(rawSession) as Partial<StoredSession>;
      return parsedSession.operatorId && parsedSession.fullName
        ? { operatorId: parsedSession.operatorId, fullName: parsedSession.fullName }
        : null;
    } catch {
      this.storage?.removeItem(this.sessionStorageKey);
      return null;
    }
  }

  private readStoredAccounts(): RegisteredOperator[] {
    const rawAccounts = this.storage?.getItem(this.accountsStorageKey);

    if (!rawAccounts) {
      return [];
    }

    try {
      const parsedAccounts = JSON.parse(rawAccounts) as RegisteredOperator[];
      return Array.isArray(parsedAccounts) ? parsedAccounts : [];
    } catch {
      this.storage?.removeItem(this.accountsStorageKey);
      return [];
    }
  }

  private persistSession(session: StoredSession): void {
    this.storage?.setItem(this.sessionStorageKey, JSON.stringify(session));
  }

  private persistAccounts(accounts: RegisteredOperator[]): void {
    this.storage?.setItem(this.accountsStorageKey, JSON.stringify(accounts));
  }

  private createGoogleOperatorId(googleId: string, email: string): string {
    const candidate =
      googleId.slice(-6) ||
      email.replace(/[^a-z0-9]/gi, '').toUpperCase().slice(0, 6) ||
      'GOOGLE';

    return `GOOGLE-${candidate.toUpperCase()}`;
  }
}
