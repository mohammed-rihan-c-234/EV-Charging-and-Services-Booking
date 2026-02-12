# EV Service Platform - Template Integration Plan

## Overview
This document outlines how to integrate the Agentix Next.js template design into the Django-based EV Service platform.

---

## Current Project Structure

### Django Apps
- **accounts**: User registration, login, profiles
- **vehicles**: Vehicle management and tracking
- **bookings**: Service bookings and reservations
- **services**: Service types and management
- **charging**: Charging station locations and availability
- **service_center**: Service center management
- **spareparts**: Spare parts inventory
- **sos**: Emergency SOS alerts
- **chatbox**: Real-time chat support
- **maps**: Location and mapping features
- **rewards**: Eco-driving rewards system

### Key Models
- User (Django built-in)
- Profile (user role: user or service_center)
- Vehicle (owner information, make, model, year, license plate)
- ServiceType (charging, maintenance, towing)
- ServiceBooking (pending, confirmed, completed)

---

## Template Analysis (Agentix Next.js)

### Structure
```
agentix-nextjs/
├── app/              (Next.js app directory with layout and main page)
├── components/       (Reusable UI components)
├── sections/         (Full-width page sections)
├── public/assets/    (Static images and icons)
```

### Key Components
- **navbar.jsx**: Navigation header
- **footer.jsx**: Footer section
- **hero-section.jsx**: Hero/banner section
- **about-our-apps.jsx**: Feature overview
- **our-latest-creation.jsx**: Showcase section
- **our-testimonials.jsx**: User testimonials
- **subscribe-newsletter.jsx**: Newsletter signup
- **get-in-touch.jsx**: Contact section
- **trusted-companies.jsx**: Partner companies
- **tilt-image.jsx**: Interactive tilting images
- **lenis-scroll.jsx**: Smooth scrolling effect
- **section-title.jsx**: Section headers

### Styling
- PostCSS with Tailwind CSS likely (based on postcss.config.mjs)
- Modern, clean design with animations
- Responsive mobile-first approach

---

## Integration Strategy

### Phase 1: Template Design Adaptation
**Goal**: Convert Next.js React components to Django template language (HTML + Django tags)

1. **Convert Components to Partials**
   - navbar.jsx → `templates/includes/navbar.html`
   - footer.jsx → `templates/includes/footer.html`
   - section-title.jsx → `templates/includes/section_title.html`
   - Other components → Reusable template includes

2. **Convert Page Sections**
   - hero-section → Homepage hero banner with EV context
   - about-our-apps → Feature overview (SOS, Chatbox, Charging, etc.)
   - our-latest-creation → Latest service offerings
   - our-testimonials → User testimonials/reviews
   - get-in-touch → Contact/support section
   - trusted-companies → Partner service centers

### Phase 2: Data Integration
**Goal**: Connect template to Django views and models

1. **Homepage (home.html)**
   - Hero section with EV-specific messaging
   - Quick stats (total vehicles, available services, etc.)
   - User dashboard overview
   - Recent bookings/services
   - Testimonials from real users

2. **Features/Services Page**
   - SOS Emergency Service
   - Charging Station Locator
   - Service Center Booking
   - Spare Parts Management
   - Rewards System
   - Real-time Chat Support

3. **User Dashboard Pages**
   - Vehicle management
   - Booking history
   - Upcoming services
   - Rewards points
   - Profile settings

4. **Public Pages**
   - About platform
   - Services overview
   - Service centers directory
   - How to use guide
   - Testimonials/Reviews

### Phase 3: Navigation & URL Mapping

**Public Routes** (No login required)
```
/ → Home page with hero section
/about → About platform
/services → Services overview
/service-centers → Directory of service centers
/contact → Contact/Support
/testimonials → User reviews
```

**Authenticated Routes** (Login required)
```
/dashboard/ → User dashboard (vehicles, bookings, rewards)
/vehicles/ → Vehicle management
/bookings/ → Service bookings
/charging/ → Charging stations
/services/ → Available services
/service-center/dashboard/ → Service center admin (conditional)
/sos/ → Emergency SOS
/chatbox/ → Support chat
/rewards/ → Rewards points
/spareparts/ → Spare parts store
```

### Phase 4: Styling System

1. **CSS Framework**
   - Keep existing Bootstrap 5 base in base.html
   - OR migrate to Tailwind CSS for consistency with template
   - Use CSS Variables for theme management (already in base.html)

2. **Assets**
   - Copy template images from agentix → `static/images/`
   - Create app-specific asset folders
   - Optimize images for web

3. **Responsive Design**
   - Mobile-first approach
   - Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
   - Touch-friendly navigation and buttons

### Phase 5: Implementation Sequence

1. **Setup**
   - Copy template assets to static/
   - Create includes/ folder for partial templates
   - Set up CSS framework (keep Bootstrap or switch to Tailwind)

2. **Navigation & Layout**
   - Create new navbar with EV branding
   - Create footer with app links
   - Update base.html to use new nav/footer

3. **Homepage**
   - Create hero section
   - Add features overview
   - Add testimonials section
   - Add newsletter signup

4. **Feature Pages**
   - Services showcase
   - Service centers directory
   - About page
   - Contact page

5. **User Features** (Connect to existing Django apps)
   - Dashboard with vehicle overview
   - Service bookings interface
   - Charging station locator (with maps integration)
   - SOS interface
   - Chatbox interface
   - Spare parts store
   - Rewards dashboard

6. **Authentication Pages**
   - Login (styled with template design)
   - Registration (styled with template design)
   - Profile management

---

## File Structure Plan

```
templates/
├── base.html (updated with new navbar/footer)
├── home.html (new hero + dashboard)
├── includes/
│   ├── navbar.html (new navigation)
│   ├── footer.html (new footer)
│   ├── hero_section.html
│   ├── features_section.html
│   ├── testimonials_section.html
│   ├── newsletter_section.html
│   └── section_title.html
├── public/
│   ├── about.html
│   ├── services.html
│   ├── service_centers.html
│   ├── contact.html
│   └── testimonials.html
├── accounts/
│   ├── login.html (updated styling)
│   ├── register.html (updated styling)
│   └── profile.html
├── vehicles/ (updated styling)
├── bookings/ (updated styling)
├── charging/ (updated styling)
├── sos/ (updated styling)
├── chatbox/ (updated styling)
├── spareparts/ (updated styling)
└── rewards/ (updated styling)

static/
├── images/
│   └── (template assets)
├── css/
│   ├── template.css (new template styles)
│   └── theme.css (theme variables)
└── js/
    └── template.js (template interactivity)
```

---

## Key Features to Highlight

### EV-Specific Features
- **SOS Emergency**: Quick access to emergency services
- **Charging Locator**: Real-time charging station availability
- **Service Centers**: Book and track maintenance
- **Spare Parts**: Order genuine parts with tracking
- **Rewards System**: Eco-friendly driving incentives
- **Chat Support**: Real-time assistance
- **Vehicle Management**: Track multiple EVs

---

## Next Steps

1. Export/Copy template source files (HTML, CSS, images)
2. Adapt components to Django template language
3. Create Django context data from models
4. Test responsive design on mobile/tablet
5. Integrate with existing Django apps
6. Add form validation and error handling
7. Implement user authentication flows

---

## Resources Needed

- Template source files (JSX components, CSS)
- Template images and assets
- Tailwind or Bootstrap configuration (if switching frameworks)
- Brand colors and typography specifications
- Any custom fonts or icons

