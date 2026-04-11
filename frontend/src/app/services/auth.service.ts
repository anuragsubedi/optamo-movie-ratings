import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { LoginRequest, LoginResponse } from '../models/movie.model';
import { environment } from '../../environments/environment';

/**
 * Authentication service.
 *
 * Manages JWT token lifecycle: login, token storage (localStorage),
 * authentication state, and logout.
 */
@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly TOKEN_KEY = 'auth_token';
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(
    this.hasToken()
  );

  /** Observable of current authentication state. */
  isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(private http: HttpClient) {}

  /**
   * Authenticate with username/password credentials.
   * Stores the returned JWT token and updates auth state.
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/login`, credentials)
      .pipe(
        tap((response) => {
          localStorage.setItem(this.TOKEN_KEY, response.token);
          this.isAuthenticatedSubject.next(true);
        })
      );
  }

  /** Remove stored token and update auth state. */
  logout(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    this.isAuthenticatedSubject.next(false);
  }

  /** Retrieve the stored JWT token. */
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /** Check if a token exists in storage. */
  private hasToken(): boolean {
    return !!localStorage.getItem(this.TOKEN_KEY);
  }
}
