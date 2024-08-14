```
interface FeatureFlags {
  [key: string]: boolean;
}

interface ConfigData {
  env: string;
  featureFlags: FeatureFlags;
  // Add other fields that are part of configData, e.g.:
  // callbackUrl?: string;
  // apiBaseUrl?: string;
}

interface AppConfig {
  configData: ConfigData;
  // Add other fields that are part of AppConfig, e.g.:
  // configName?: string;
}



import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, firstValueFrom } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

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
      
      const config = await firstValueFrom(
        this.http.get<AppConfig>(this.API_SPRING_URL + this.endPoint).pipe(
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
              const parsedConfig = JSON.parse(cachedConfig) as AppConfig;
              this.configSubject.next(parsedConfig);
              return parsedConfig;
            } else {
              console.warn('No cached configuration found.');
              throw err;
            }
          })
        )
      );

      // Ensure the environment is set first
      if (config?.configData?.env) {
        this.setEnvironment(config.configData.env);
        console.log("Environment set to:", config.configData.env);
      } else {
        console.error('Environment value is missing in the configuration:', config);
        throw new Error('Environment value is missing in the configuration');
      }

      // Store feature flags individually
      if (config?.configData?.featureFlags) {
        Object.entries(config.configData.featureFlags).forEach(([key, value]) => {
          localStorage.setItem(key, JSON.stringify(value));
        });
      }

      return config;
    } catch (err) {
      console.error('Error during configuration loading:', err);
      throw err; // Ensure that errors are properly rethrown
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

    if (!config) {
      console.warn('Config not loaded when checking for feature flag');
      return false;
    }

    return config.configData?.featureFlags?.[featureName] ?? false;
  }
}

--------------------




import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';

interface AppConfig {
  env: string;
  // Add other config properties here
}

interface FeatureFlags {
  [key: string]: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private readonly API_SPRING_URL = environment.API_SPRING_URL;
  private readonly CONFIG_ENDPOINT = '/ui-config/ui-settings';
  private readonly CONFIG_CACHE_KEY = 'appConfig';
  private readonly FEATURE_FLAGS_CACHE_KEY = 'featureFlags';

  private configSubject = new BehaviorSubject<AppConfig | null>(null);
  private featureFlagsSubject = new BehaviorSubject<FeatureFlags | null>(null);

  constructor(private http: HttpClient) {}

  loadConfig(): Observable<AppConfig> {
    return this.http.get<AppConfig>(`${this.API_SPRING_URL}${this.CONFIG_ENDPOINT}`).pipe(
      tap(config => this.handleNewConfig(config)),
      catchError(error => this.handleConfigError(error))
    );
  }

  private handleNewConfig(config: AppConfig): void {
    this.configSubject.next(config);
    this.cacheConfig(config);
    this.updateFeatureFlags(config);
    this.setEnvironment(config.env);
  }

  private handleConfigError(error: any): Observable<AppConfig> {
    console.error('Failed to load configuration:', error);
    const cachedConfig = this.loadCachedConfig();
    if (cachedConfig) {
      console.log('Using cached configuration');
      this.handleNewConfig(cachedConfig);
      return of(cachedConfig);
    }
    throw new Error('No configuration available');
  }

  private cacheConfig(config: AppConfig): void {
    localStorage.setItem(this.CONFIG_CACHE_KEY, JSON.stringify(config));
  }

  private loadCachedConfig(): AppConfig | null {
    const cached = localStorage.getItem(this.CONFIG_CACHE_KEY);
    return cached ? JSON.parse(cached) : null;
  }

  private updateFeatureFlags(config: AppConfig): void {
    const featureFlags = (config as any).featureFlags as FeatureFlags;
    if (featureFlags) {
      this.featureFlagsSubject.next(featureFlags);
      this.cacheFeatureFlags(featureFlags);
    }
  }

  private cacheFeatureFlags(featureFlags: FeatureFlags): void {
    localStorage.setItem(this.FEATURE_FLAGS_CACHE_KEY, JSON.stringify(featureFlags));
  }

  private setEnvironment(env: string): void {
    if (env) {
      sessionStorage.setItem('env', env);
      console.log('Environment set:', env);
    }
  }

  getConfig(): Observable<AppConfig | null> {
    return this.configSubject.asObservable();
  }

  getFeatureFlags(): Observable<FeatureFlags | null> {
    return this.featureFlagsSubject.asObservable();
  }

  isFeatureEnabled(featureName: string): Observable<boolean> {
    return this.getFeatureFlags().pipe(
      map(flags => flags ? !!flags[featureName] : false)
    );
  }
}

-----------------
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ConfigService } from './config.service';
import { map } from 'rxjs/operators';

// Components
import { HomeComponent } from './home.component';
import { FeatureAComponent } from './feature-a.component';
import { FeatureBComponent } from './feature-b.component';

// Route guard
import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FeatureFlagGuard implements CanActivate {
  constructor(private configService: ConfigService) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> {
    const requiredFeature = route.data['requiredFeature'] as string;
    return this.configService.isFeatureEnabled(requiredFeature);
  }
}

// Routing configuration
const routes: Routes = [
  { path: '', component: HomeComponent },
  { 
    path: 'feature-a', 
    component: FeatureAComponent,
    canActivate: [FeatureFlagGuard],
    data: { requiredFeature: 'featureA' }
  },
  { 
    path: 'feature-b', 
    component: FeatureBComponent,
    canActivate: [FeatureFlagGuard],
    data: { requiredFeature: 'featureB' }
  },
  // Dynamic route based on configuration
  {
    path: 'dynamic',
    loadChildren: () => 
      import('./dynamic/dynamic.module').then(m => m.DynamicModule),
    canLoad: [DynamicModuleGuard]
  }
];

@Injectable({
  providedIn: 'root'
})
class DynamicModuleGuard  {
  constructor(private configService: ConfigService) {}

  canLoad(): Observable<boolean> {
    return this.configService.getConfig().pipe(
      map(config => config?.enableDynamicModule ?? false)
    );
  }
}

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
  constructor(private configService: ConfigService) {
    // You can also dynamically modify routes here based on config
    this.configService.getConfig().subscribe(config => {
      if (config?.additionalRoutes) {
        // Logic to add routes dynamically
      }
    });
  }
}
```
