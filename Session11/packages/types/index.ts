// Shared DTOs and interfaces used by both client and server

export type DayOfWeek = 'mon' | 'tue' | 'wed' | 'thu' | 'fri' | 'sat' | 'sun';

export interface WorkingHoursSlot {
  start: string;
  end: string;
}

export type WorkingHours = Record<DayOfWeek, WorkingHoursSlot>;

export interface Service {
  name: string;
  durationMinutes: number;
  price: number;
}

export interface Business {
  _id: string;
  name: string;
  email: string;
  phoneNumber: string;
  services: Service[];
  workingHours: WorkingHours;
  timezone: string;
  vapiAssistantId?: string;
  createdAt: string;
}

export type AppointmentStatus = 'booked' | 'cancelled' | 'completed' | 'no-show';
export type AppointmentSource = 'ai-call' | 'manual';

export interface Appointment {
  _id: string;
  businessId: string;
  customerName: string;
  customerPhone: string;
  service: string;
  date: string;
  startTime: string;
  endTime: string;
  status: AppointmentStatus;
  source: AppointmentSource;
  callId?: string;
  notes?: string;
  createdAt: string;
}

export interface Customer {
  _id: string;
  businessId: string;
  name: string;
  phone: string;
  history: string[];
  totalVisits: number;
}

export interface AvailabilityRequest {
  businessId: string;
  serviceName: string;
  date: string;
}

export interface AvailabilitySlot {
  startTime: string;
  endTime: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  business: Omit<Business, 'vapiAssistantId'>;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

export interface DashboardStats {
  totalToday: number;
  upcoming: number;
  cancelled: number;
}

export interface VapiCheckAvailabilityPayload {
  businessId: string;
  serviceName: string;
  date: string;
}

export interface VapiBookAppointmentPayload {
  businessId: string;
  customerName: string;
  customerPhone: string;
  service: string;
  date: string;
  startTime: string;
  callId?: string;
}

export interface VapiCancelAppointmentPayload {
  businessId: string;
  appointmentId: string;
}

export interface SocketAppointmentEvent {
  appointment: Appointment;
}
