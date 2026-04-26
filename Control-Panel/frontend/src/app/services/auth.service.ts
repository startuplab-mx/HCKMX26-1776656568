import { Injectable, signal } from '@angular/core';

type StoredSession = {
  operatorId: string;
};

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly sessionStorageKey = 'guardian.control.session';
  private readonly demoCredentials = {
    operatorId: 'OPS-2048',
    accessKey: 'guardian404'
  } as const;
  private readonly sessionState = signal<StoredSession | null>(this.readStoredSession());

  readonly session = this.sessionState.asReadonly();

  isAuthenticated(): boolean {
    return this.sessionState() !== null;
  }

  signIn(operatorId: string, accessKey: string): boolean {
    const normalizedOperatorId = operatorId.trim().toUpperCase();
    const normalizedAccessKey = accessKey.trim();
    const isValid =
      normalizedOperatorId === this.demoCredentials.operatorId &&
      normalizedAccessKey === this.demoCredentials.accessKey;

    if (!isValid) {
      return false;
    }

    const session = { operatorId: normalizedOperatorId };
    this.sessionState.set(session);
    this.persistSession(session);
    return true;
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
      return parsedSession.operatorId ? { operatorId: parsedSession.operatorId } : null;
    } catch {
      this.storage?.removeItem(this.sessionStorageKey);
      return null;
    }
  }

  private persistSession(session: StoredSession): void {
    this.storage?.setItem(this.sessionStorageKey, JSON.stringify(session));
  }
}
