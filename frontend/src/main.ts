import { CommonModule } from '@angular/common';
import { HttpClient, provideHttpClient } from '@angular/common/http';
import { Component, Injectable, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { bootstrapApplication } from '@angular/platform-browser';
import { RouterLink, RouterOutlet, Routes, provideRouter } from '@angular/router';
import { environment } from './environments/environment';

interface Unit {
  id: number;
  tower: string;
  number: string;
  bedrooms: number;
  rent: number;
  occupied: boolean;
  amenities: string[];
}

interface Booking {
  id: number;
  unit_number: string;
  resident: string;
  move_in_date: string;
  status: string;
  mock_payment_status: string;
}

@Injectable({ providedIn: 'root' })
class ApiService {
  private http = inject(HttpClient);
  private token = '';

  setToken(token: string): void {
    this.token = token;
  }

  login(email: string, password: string) {
    return this.http.post<{ access_token: string }>(`${environment.apiBaseUrl}/auth/login`, { email, password });
  }

  getUnits() {
    return this.http.get<Unit[]>(`${environment.apiBaseUrl}/units`);
  }

  getMyBookings() {
    return this.http.get<Booking[]>(`${environment.apiBaseUrl}/bookings/me`, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
  }

  createBooking(unitId: number, moveInDate: string) {
    return this.http.post(`${environment.apiBaseUrl}/bookings`, { unit_id: unitId, move_in_date: moveInDate }, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
  }

  getAdminDashboard() {
    return this.http.get<Record<string, string | number>>(`${environment.apiBaseUrl}/admin/dashboard`, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
  }

  getAdminBookings() {
    return this.http.get<Booking[]>(`${environment.apiBaseUrl}/admin/bookings`, {
      headers: { Authorization: `Bearer ${this.token}` }
    });
  }
}

@Component({
  selector: 'resident-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="p-6 space-y-4">
      <h2 class="text-2xl font-bold">Resident Portal</h2>
      <div class="bg-white rounded-xl p-4 shadow">
        <h3 class="font-semibold mb-2">Available Units</h3>
        <div *ngFor="let unit of units" class="border-b py-2">
          <div>{{ unit.tower }} - {{ unit.number }} | {{ unit.bedrooms }} BR | ${{ unit.rent }}</div>
          <div class="text-sm text-gray-600">Amenities: {{ unit.amenities.join(', ') }}</div>
        </div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow space-y-2">
        <h3 class="font-semibold">Request Booking</h3>
        <input [(ngModel)]="unitId" placeholder="Unit ID" class="border p-2 rounded w-full" />
        <input [(ngModel)]="moveInDate" type="date" class="border p-2 rounded w-full" />
        <button (click)="submitBooking()" class="bg-blue-600 text-white px-4 py-2 rounded">Submit</button>
        <p class="text-sm text-green-700">{{ message }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow">
        <h3 class="font-semibold">My Bookings</h3>
        <div *ngFor="let booking of bookings" class="py-2 border-b">
          {{ booking.unit_number }} · {{ booking.move_in_date }} · {{ booking.status }} · Payment: {{ booking.mock_payment_status }}
        </div>
      </div>
    </section>
  `
})
class ResidentPage {
  private api = inject(ApiService);
  units: Unit[] = [];
  bookings: Booking[] = [];
  unitId = '';
  moveInDate = '';
  message = '';

  ngOnInit(): void {
    this.api.getUnits().subscribe((units) => {
      this.units = units;
    });
    this.refreshBookings();
  }

  submitBooking(): void {
    this.api.createBooking(Number(this.unitId), this.moveInDate).subscribe(() => {
      this.message = 'Booking request submitted';
      this.refreshBookings();
    });
  }

  refreshBookings(): void {
    this.api.getMyBookings().subscribe((bookings) => {
      this.bookings = bookings;
    });
  }
}

@Component({
  selector: 'admin-page',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="p-6 space-y-4">
      <h2 class="text-2xl font-bold">Admin Portal</h2>
      <div class="grid grid-cols-2 gap-4">
        <div class="bg-white rounded-xl p-4 shadow" *ngFor="let item of statEntries()">
          <div class="text-sm text-gray-500">{{ item.key }}</div>
          <div class="text-2xl font-bold">{{ item.value }}</div>
        </div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow">
        <h3 class="font-semibold mb-2">Booking Queue</h3>
        <div *ngFor="let booking of bookings" class="py-2 border-b">
          {{ booking.resident }} requested {{ booking.unit_number }} on {{ booking.move_in_date }} → {{ booking.status }}
        </div>
      </div>
    </section>
  `
})
class AdminPage {
  private api = inject(ApiService);
  stats: Record<string, string | number> = {};
  bookings: Booking[] = [];

  ngOnInit(): void {
    this.api.getAdminDashboard().subscribe((stats) => {
      this.stats = stats;
    });
    this.api.getAdminBookings().subscribe((bookings) => {
      this.bookings = bookings;
    });
  }

  statEntries(): Array<{ key: string; value: string | number }> {
    return Object.entries(this.stats).map(([key, value]) => ({ key, value }));
  }
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, CommonModule, FormsModule],
  template: `
    <main class="min-h-screen">
      <header class="bg-slate-900 text-white px-6 py-4 flex justify-between items-center">
        <h1 class="font-bold">Residential Apartment Rental Portal</h1>
        <nav class="space-x-4">
          <a routerLink="/resident" class="hover:underline">Resident</a>
          <a routerLink="/admin" class="hover:underline">Admin</a>
        </nav>
      </header>
      <section class="p-6 bg-white shadow mx-6 mt-6 rounded-xl max-w-xl">
        <h2 class="font-semibold mb-3">Demo Login</h2>
        <input [(ngModel)]="email" placeholder="Email" class="border p-2 rounded w-full mb-2" />
        <input [(ngModel)]="password" type="password" placeholder="Password" class="border p-2 rounded w-full mb-2" />
        <button (click)="login()" class="bg-emerald-600 text-white px-4 py-2 rounded">Sign in</button>
        <p class="text-sm mt-2">{{ loginStatus }}</p>
      </section>
      <router-outlet></router-outlet>
    </main>
  `
})
class AppComponent {
  private api = inject(ApiService);
  email = 'resident@portal.local';
  password = 'Resident@123';
  loginStatus = 'Use demo credentials from README.';

  login(): void {
    this.api.login(this.email, this.password).subscribe({
      next: (response) => {
        this.api.setToken(response.access_token);
        this.loginStatus = 'Authenticated successfully.';
      },
      error: () => {
        this.loginStatus = 'Login failed. Verify credentials.';
      }
    });
  }
}

const routes: Routes = [
  { path: '', redirectTo: 'resident', pathMatch: 'full' },
  { path: 'resident', component: ResidentPage },
  { path: 'admin', component: AdminPage }
];

bootstrapApplication(AppComponent, {
  providers: [provideHttpClient(), provideRouter(routes)]
}).catch((error: unknown) => {
  console.error(error);
});
