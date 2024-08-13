```
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, firstValueFrom } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private configSubject = new BehaviorSubject<any>(null);
  public config$ = this.configSubject.asObservable();

  constructor(private http: HttpClient) {}

  public async loadConfig() {
    try {
      console.log('Attempting to load configuration from /api/ui-config/ui-settings');
      
      const data = await firstValueFrom(
        this.http.get('/api/ui-config/ui-settings').pipe(
          tap(config => {
            console.log('Configuration loaded successfully:', config);
            this.configSubject.next(config);
            localStorage.setItem('appConfig', JSON.stringify(config));
          }),
          catchError(err => {
            console.error('Failed to load configuration from server:', err);

            const cachedConfig = localStorage.getItem('appConfig');
            if (cachedConfig) {
              console.log('Using cached configuration:', cachedConfig);
              this.configSubject.next(JSON.parse(cachedConfig));
            } else {
              console.warn('No cached configuration found.');
            }

            throw err;
          })
        )
      );

      this.setEnvironment(data['ENV']);
      console.log("Environment set to: " + data['ENV']);
      return data;
    } catch (err) {
      console.error('Error during configuration loading:', err);
    }
  }

  private setEnvironment(env: string) {
    if (env) {
      sessionStorage.setItem("ENV", env);
      console.log("Environment saved to session storage:", env);
    } else {
      console.warn("No environment value provided; session storage not updated.");
    }
  }

  public getConfig() {
    const config = this.configSubject.value;
    console.log('Current configuration:', config);
    return config;
  }

  public isFeatureEnabled(featureName: string): boolean {
    const config = this.getConfig();
    const isEnabled = config?.featureFlags?.[featureName] ?? false;
    console.log(`Feature "${featureName}" enabled:`, isEnabled);
    return isEnabled;
  }
}

```
