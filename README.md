```
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatAdminDashboardComponent } from './mat-admin-dashboard.component';
import { MatAdminUsersComponent } from './mat-admin-users.component';

const routes: Routes = [
  { path: '', component: MatAdminDashboardComponent },
  { path: 'users', component: MatAdminUsersComponent }
];

@NgModule({
  declarations: [MatAdminDashboardComponent, MatAdminUsersComponent],
  imports: [
    CommonModule,
    MatButtonModule,
    MatToolbarModule,
    RouterModule.forChild(routes)
  ]
})
export class MatAdminModule { }



import { Component } from '@angular/core';

@Component({
  selector: 'app-mat-admin-dashboard',
  template: `
    <mat-toolbar color="primary">Material Admin Dashboard</mat-toolbar>
    <div style="padding: 20px;">
      <h2>Welcome to Material Admin Dashboard</h2>
      <button mat-raised-button color="primary" routerLink="users">Go to Users</button>
    </div>
  `
})
export class MatAdminDashboardComponent { }


import { Component } from '@angular/core';

@Component({
  selector: 'app-mat-admin-users',
  template: `
    <mat-toolbar color="primary">Material Admin Users</mat-toolbar>
    <div style="padding: 20px;">
      <h2>Material Admin Users List</h2>
      <button mat-raised-button color="primary" routerLink="..">Back to Dashboard</button>
    </div>
  `
})
export class MatAdminUsersComponent { }


import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { ButtonModule } from '@syncfusion/ej2-angular-buttons';
import { SyncAdminDashboardComponent } from './sync-admin-dashboard.component';
import { SyncAdminUsersComponent } from './sync-admin-users.component';

const routes: Routes = [
  { path: '', component: SyncAdminDashboardComponent },
  { path: 'users', component: SyncAdminUsersComponent }
];

@NgModule({
  declarations: [SyncAdminDashboardComponent, SyncAdminUsersComponent],
  imports: [
    CommonModule,
    ButtonModule,
    RouterModule.forChild(routes)
  ]
})
export class SyncAdminModule { }



import { Component } from '@angular/core';

@Component({
  selector: 'app-sync-admin-dashboard',
  template: `
    <div style="background-color: #007bff; color: white; padding: 10px;">Syncfusion Admin Dashboard</div>
    <div style="padding: 20px;">
      <h2>Welcome to Syncfusion Admin Dashboard</h2>
      <ejs-button cssClass="e-primary" routerLink="users">Go to Users</ejs-button>
    </div>
  `
})
export class SyncAdminDashboardComponent { }


import { Component } from '@angular/core';

@Component({
  selector: 'app-sync-admin-users',
  template: `
    <div style="background-color: #007bff; color: white; padding: 10px;">Syncfusion Admin Users</div>
    <div style="padding: 20px;">
      <h2>Syncfusion Admin Users List</h2>
      <ejs-button cssClass="e-primary" routerLink="..">Back to Dashboard</ejs-button>
    </div>
  `
})
export class SyncAdminUsersComponent { }




import { NgModule, inject } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ConfigService } from './config.service';

const routes: Routes = [
  // ... other routes ...
  {
    path: 'admin',
    loadChildren: () => {
      const configService = inject(ConfigService);
      return configService.isFeatureEnabled('useMaterialAdmin')
        ? import('./mat-admin/mat-admin.module').then(m => m.MatAdminModule)
        : import('./sync-admin/sync-admin.module').then(m => m.SyncAdminModule);
    }
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
```
