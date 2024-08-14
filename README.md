
```
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, firstValueFrom } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private API_SPRING_URL = environment.API_SPRING_URL;
  private endPoint = '/ui-config/ui-settings';

  private configSubject = new BehaviorSubject<AppConfig | null>(null);
  public config$ = this.configSubject.asObservable();

  constructor(private http: HttpClient) {}

  public async loadConfig() {
    try {
      console.log('Attempting to load configuration from /api/ui-config/ui-settings');
      
      const config: AppConfig = await firstValueFrom(
        this.http.get<AppConfig>(this.API_SPRING_URL + this.endPoint).pipe(
          catchError(err => {
            console.error('Failed to load configuration from server:', err);

            const cachedConfig = localStorage.getItem('appConfig');
            if (cachedConfig) {
              console.log('Using cached configuration:', cachedConfig);
              return JSON.parse(cachedConfig) as AppConfig;
            } else {
              console.warn('No cached configuration found.');
              throw err;
            }
          })
        )
      );

      // Store processed data once
      this.setEnvironment(config.configData.env);
      console.log("Environment set to:", config.configData.env);

      // Store feature flags individually
      if (config.configData && config.configData.featureFlags) {
        Object.entries(config.configData.featureFlags).forEach(([key, value]) => {
          localStorage.setItem(key, JSON.stringify(value));
        });
      }

      // Optionally, store the whole config if needed for other purposes
      localStorage.setItem('appConfig', JSON.stringify(config));

      this.configSubject.next(config);
      return config;
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
    const config = this.configSubject.getValue();

    if (!config || !config.configData || !config.configData.featureFlags) {
      console.warn('Config or feature flags not loaded when checking for feature flag');
      return false;
    }

    return config.configData.featureFlags[featureName] ?? false;
  }
}

interface FeatureFlags {
  useMaterialAdmin: boolean;
  enableDarkMode: boolean;
  enableMaterial: boolean;
  [key: string]: boolean; // To allow additional feature flags
}

interface ConfigData {
  env: string;
  callbackUrl: string;
  apiBaseUrl: string;
  featureFlags: FeatureFlags;
}

interface AppConfig {
  configName: string;
  configData: ConfigData;
}


```
