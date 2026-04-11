import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

/**
 * Route guard that prevents unauthenticated access to protected routes.
 *
 * Redirects to /login if no valid token is present.
 * Uses the functional guard pattern (Angular 15+).
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.getToken()) {
    return true;
  }

  router.navigate(['/login']);
  return false;
};
