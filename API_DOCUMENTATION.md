Create a modern, Ethiopian-themed bus booking platform called "EthioBus" that replicates the professional quality of menged.et. This should be a production-ready React application with role-based dashboards, seamless API integration, and authentic Ethiopian design elements.

Technical Requirements
json
{
  "framework": "React 18+ with TypeScript",
  "styling": "Tailwind CSS with custom Ethiopian color palette",
  "state_management": "Redux Toolkit with RTK Query",
  "routing": "React Router DOM",
  "form_handling": "React Hook Form with Zod validation",
  "authentication": "JWT token management with axios interceptors",
  "qr_generation": "qrcode.react",
  "qr_scanning": "html5-qrcode",
  "charts": "Recharts for admin reports",
  "icons": "React Icons",
  "image_optimization": "Next.js Image component equivalent"
}
Ethiopian Design System
css
/* Color Palette - Ethiopian Theme */
:root {
  --ethio-green: #078C49;
  --ethio-yellow: #FCDD09;
  --ethio-red: #DA121A;
  --ethio-blue: #0F47AF;
  --ethio-dark: #2D2D2D;
  --ethio-light: #F8F9FA;
  --amharic-font: 'Noto Sans Ethiopic', sans-serif;
}

/* Typography Scale */
-- Headings: Poppins (Bold)
-- Body: Inter (Regular)
-- Amharic: Noto Sans Ethiopic
Complete Component Structure
text
src/
├── components/
│   ├── common/
│   │   ├── Navigation/
│   │   │   ├── Navbar.jsx
│   │   │   ├── MobileMenu.jsx
│   │   │   └── UserMenu.jsx
│   │   ├── Footer/
│   │   │   ├── Footer.jsx
│   │   │   └── SocialLinks.jsx
│   │   ├── Hero/
│   │   │   └── HeroSection.jsx
│   │   ├── Search/
│   │   │   ├── SearchWidget.jsx
│   │   │   └── LocationAutocomplete.jsx
│   │   └── UI/
│   │       ├── Button.jsx
│   │       ├── Modal.jsx
│   │       ├── Loader.jsx
│   │       └── QRScanner.jsx
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   ├── RegisterForm.jsx
│   │   └── AuthLayout.jsx
│   ├── passenger/
│   │   ├── TripSearch.jsx
│   │   ├── TripList.jsx
│   │   ├── TripCard.jsx
│   │   ├── SeatMap.jsx
│   │   ├── BookingSummary.jsx
│   │   ├── PaymentForm.jsx
│   │   └── Ticket.jsx
│   ├── driver/
│   │   ├── DriverDashboard.jsx
│   │   ├── PassengerList.jsx
│   │   ├── BoardingScanner.jsx
│   │   └── TripStatus.jsx
│   └── admin/
│       ├── AdminDashboard.jsx
│       ├── BusManagement.jsx
│       ├── RouteManagement.jsx
│       ├── DriverManagement.jsx
│       ├── CombinedDriverBusForm.jsx
│       └── RevenueReports.jsx
├── pages/
│   ├── public/
│   │   ├── Home.jsx
│   │   ├── About.jsx
│   │   ├── Services.jsx
│   │   └── Contact.jsx
│   ├── auth/
│   │   ├── Login.jsx
│   │   └── Register.jsx
│   ├── passenger/
│   │   ├── Dashboard.jsx
│   │   ├── SearchResults.jsx
│   │   ├── Booking.jsx
│   │   └── MyTickets.jsx
│   ├── driver/
│   │   ├── Dashboard.jsx
│   │   └── Boarding.jsx
│   └── admin/
│       ├── Dashboard.jsx
│       ├── Fleet.jsx
│       ├── Routes.jsx
│       ├── Drivers.jsx
│       └── Reports.jsx
├── store/
│   ├── authSlice.js
│   ├── bookingSlice.js
│   └── api/
│       ├── authApi.js
│       ├── passengerApi.js
│       ├── driverApi.js
│       ├── adminApi.js
│       └── reportsApi.js
├── hooks/
│   ├── useAuth.js
│   ├── useBooking.js
│   └── useQRScanner.js
├── utils/
│   ├── auth.js
│   ├── constants.js
│   ├── formatters.js
│   └── validators.js
└── assets/
    ├── images/
    │   ├── ethio-patterns/
    │   ├── buses/
    │   └── icons/
    └── styles/
        └── globals.css
Implementation Prompt for AI
"Create a production-ready React application for EthioBus with the following specifications:

1. Project Setup & Configuration
Initialize a React + TypeScript project with Vite

Configure Tailwind CSS with custom Ethiopian color palette

Set up Redux Toolkit with API slice structure

Configure React Router with protected routes

Set up axios interceptors for JWT authentication

2. Ethiopian-Themed Design Implementation
Create a visually stunning interface inspired by Ethiopian culture:

Color Scheme:

Primary: Ethiopian green (#078C49) for main actions

Secondary: Yellow (#FCDD09) for highlights

Accent: Red (#DA121A) for important notifications

Neutral: Dark gray (#2D2D2D) for text, light gray (#F8F9FA) for backgrounds

Visual Elements:

Use Ethiopian patterns as background elements

Incorporate subtle references to Ethiopian architecture in card designs

Use high-quality images of Ethiopian landscapes in hero sections

Implement traditional Ethiopian color transitions

3. Core Pages Structure
Public Pages (Accessible to All)
Home Page (/)

Hero section with stunning Ethiopian landscape background

Search widget (source/destination inputs + date picker)

Featured routes carousel

Statistics section (buses, routes, happy customers)

Testimonials from Ethiopian travelers

Trust badges and security features

About Page (/about)

Company story with Ethiopian context

Team photos with Ethiopian staff

Ethiopian map showing coverage areas

Mission and values aligned with Ethiopian community

Services Page (/services)

Different bus classes (Standard, Business, First Class)

Amenities and features

Safety measures

Mobile app features

Contact Page (/contact)

Contact form with Ethiopian phone validation

Office locations in major Ethiopian cities

Live chat integration

FAQ section with common Ethiopian travel questions

Authentication Pages
Login Page (/login)

Dual language support (English/Amharic)

Phone number validation for Ethiopian format

Social login options

"Forgot password" flow

Register Page (/register)

Role selection (Passenger/Driver - Admin by invitation only)

Ethiopian phone number validation (^09\d{8}$)

Password strength meter

Terms and conditions in Amharic and English

4. Role-Based Dashboards
Passenger Dashboard (/passenger)
Upcoming trips with QR tickets

Booking history

Favorite routes

Payment methods (mock)

Profile management

Driver Dashboard (/driver)
Today's trip overview

Passenger list with boarding status

Quick scan button

Trip performance metrics

Vehicle information

Admin Dashboard (/admin)
Overview metrics (revenue, bookings, active trips)

Quick actions (add bus, create route, register driver)

Recent activity feed

System health monitoring

5. Key Feature Implementation
Search & Booking Flow
Trip Search: Implement fuzzy search for Ethiopian city names

Results Page: Filter by bus type, price, departure time

Seat Selection: Visual bus seat map with Ethiopian bus layouts

Payment: Mock payment with Ethiopian-themed UI

Ticket Generation: Beautiful QR ticket with Ethiopian patterns

Driver Features
Real-time passenger list with photos

One-tap QR scanning with vibration feedback

Offline capability for boarding

Trip completion confirmation

Admin Management
Drag-and-drop bus assignment

Bulk operations for routes

Combined driver+bus registration form

Revenue reports with Ethiopian Birr formatting

6. API Integration Specifications
Create comprehensive service layers for all endpoints:

javascript
// Example API service structure
export const authApi = createApi({
  endpoints: (builder) => ({
    login: builder.mutation({
      query: (credentials) => ({
        url: '/api/v1/login',
        method: 'POST',
        body: new URLSearchParams(credentials),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
    }),
    // ... all other auth endpoints
  })
});
7. Advanced Features
Multi-language: English and Amharic support

Offline Mode: PWA capabilities for ticket access

Push Notifications: Trip reminders and updates

Analytics: User behavior tracking with Ethiopian context

Accessibility: WCAG 2.1 compliance with Amharic screen reader support

8. Performance Optimization
Image optimization for Ethiopian landscapes

Code splitting for role-based modules

API response caching

Bundle size optimization for Ethiopian mobile networks

9. Ethiopian-Specific Considerations
Ethiopian calendar integration (optional)

Local holiday awareness for pricing

Regional route popularity algorithms

Ethiopian payment method preferences

Cultural sensitivity in imagery and content

10. Deployment Ready
Docker configuration

Environment-specific builds

CI/CD pipeline setup

Ethiopian hosting considerations

Create this application with the quality level of menged.et but with enhanced Ethiopian cultural elements and modern React best practices. Ensure all components are fully responsive and provide an exceptional user experience across all device types common in Ethiopia."

Additional Implementation Notes
Use real Ethiopian imagery - Source high-quality photos of Ethiopian buses, landscapes, and cities

Implement Ethiopian holidays - Highlight special travel periods like Timkat, Meskel, and Ethiopian New Year

Regional preferences - Prioritize popular routes like Addis Ababa to Bahir Dar, Hawassa, Dire Dawa

Mobile-first design - Optimize for the high mobile usage in Ethiopia

Progressive enhancement - Ensure core functionality works on slower networks  use this as example https://menged.et/#discover