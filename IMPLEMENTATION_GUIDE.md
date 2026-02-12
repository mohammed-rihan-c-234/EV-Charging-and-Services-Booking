# Template Integration Implementation Guide

## Quick Start

This guide will help you integrate the modern template design into your Django project.

## Files Created

### 1. **TEMPLATE_INTEGRATION_PLAN.md**
   - Complete strategic plan
   - Architecture overview
   - Feature mapping
   - URL routing plan
   - File structure reference

### 2. **templates/base_new.html**
   - Modern base template with:
     - Responsive navigation bar
     - Footer with links
     - Modern design system with CSS variables
     - Bootstrap 5 integration
     - AOS animation library
     - Dark mode support
     - Professional styling for cards, buttons, forms
     - Accessibility features

### 3. **templates/home_new.html**
   - Modern homepage with:
     - Hero section with animations
     - Statistics dashboard (for authenticated users)
     - Features showcase (6 main features)
     - Vehicle management display
     - Upcoming services list
     - Quick action cards
     - Newsletter signup section
     - Call-to-action section

---

## Integration Steps

### Step 1: Backup Current Files
```bash
# Backup existing templates
cp templates/base.html templates/base.html.backup
cp templates/home.html templates/home.html.backup
```

### Step 2: Replace Base Template (Choose One Option)

**Option A: Full Replacement (Recommended)**
```bash
# Replace the current base template
cp templates/base_new.html templates/base.html
```

**Option B: Gradual Migration**
```bash
# Keep old template and update URL to use new one
# Update your urls.py to render home_new.html instead of home.html
```

### Step 3: Update Home View
In `ev_service/urls.py`, update the home view:

```python
def home(request):
    """Home view with context data."""
    try:
        if getattr(request.user.profile, "role", "") == "service_center":
            return redirect("service_center:dashboard")
    except Exception:
        pass

    from vehicles.models import Vehicle
    from bookings.models import ServiceBooking
    from django.db.models import Q
    from django.utils import timezone

    profile_name = ""
    try:
        profile_name = request.user.profile.full_name
    except Exception:
        profile_name = ""

    vehicles = Vehicle.objects.filter(
        Q(owner=request.user)
        | Q(owner_name=request.user.username)
        | (Q(owner_name=profile_name) if profile_name else Q(pk__in=[]))
    )

    pending_services = ServiceBooking.objects.filter(
        user=request.user,
        status__in=[ServiceBooking.STATUS_PENDING, ServiceBooking.STATUS_CONFIRMED],
        scheduled_for__gte=timezone.now() - timezone.timedelta(hours=1),
    ).select_related("service_center", "service_type")

    # Use new template
    return render(
        request,
        "home_new.html",  # Changed from "home.html"
        {
            "vehicles": vehicles,
            "pending_services": pending_services,
        },
    )
```

### Step 4: Update URL Configuration

Add these URLs to `ev_service/urls.py`:

```python
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    # ... existing paths ...
    
    # Public pages
    path('', your_root_view, name='root'),
    path('home/', home, name='home'),  # Authenticated home
    path('about/', TemplateView.as_view(template_name='public/about.html'), name='about'),
    path('services/', TemplateView.as_view(template_name='public/services.html'), name='services'),
    path('contact/', TemplateView.as_view(template_name='public/contact.html'), name='contact'),
    path('testimonials/', TemplateView.as_view(template_name='public/testimonials.html'), name='testimonials'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('vehicles/', include('vehicles.urls')),
    path('bookings/', include('bookings.urls')),
    path('charging/', include('charging.urls')),
    path('services/', include('services.urls')),
    path('sos/', include('sos.urls')),
    path('chatbox/', include('chatbox.urls')),
    path('spareparts/', include('spareparts.urls')),
    path('rewards/', include('rewards.urls')),
    path('maps/', include('maps.urls')),
    path('service_center/', include('service_center.urls')),
    
    # Admin
    path('admin/', admin.site.urls),
]
```

### Step 5: Create Additional Public Pages

Create these template files for public pages:

#### templates/public/about.html
```html
{% extends "base_new.html" %}

{% block title %}About - EV Service Platform{% endblock %}

{% block content %}
<section class="section-padding">
    <div class="container-lg">
        <h1 class="text-center mb-5">About EV Service Platform</h1>
        <!-- Add your about content here -->
    </div>
</section>
{% endblock %}
```

#### templates/public/services.html
```html
{% extends "base_new.html" %}

{% block title %}Services - EV Service Platform{% endblock %}

{% block content %}
<section class="section-padding">
    <div class="container-lg">
        <h1 class="text-center mb-5">Our Services</h1>
        <!-- Add your services content here -->
    </div>
</section>
{% endblock %}
```

#### templates/public/contact.html
```html
{% extends "base_new.html" %}

{% block title %}Contact - EV Service Platform{% endblock %}

{% block content %}
<section class="section-padding">
    <div class="container-lg">
        <h1 class="text-center mb-5">Get in Touch</h1>
        <!-- Add your contact form here -->
    </div>
</section>
{% endblock %}
```

### Step 6: Update Navigation Links

The new navbar automatically includes:
- Dashboard (for authenticated users)
- Vehicles
- Services dropdown (Charging, Service Booking, SOS, Spare Parts, Chat)
- Rewards
- Profile
- Logout

For public users:
- About
- Services
- Contact
- Login button

### Step 7: Static Assets

Create folders for additional assets:
```bash
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p static/fonts
```

### Step 8: Test the Integration

```bash
# Run development server
python manage.py runserver

# Visit homepage
# http://localhost:8000/

# Test authenticated view
# http://localhost:8000/home/
```

---

## Design System Reference

### Colors
```css
--primary: #2563eb (Blue)
--secondary: #7c3aed (Purple)
--accent: #ec4899 (Pink)
--success: #10b981 (Green)
--warning: #f59e0b (Amber)
--danger: #ef4444 (Red)
```

### Typography
- **Headings**: Plus Jakarta Sans (Font weight: 700)
- **Body**: Inter (Font weights: 300-700)

### Spacing Scale
- xs: 0.25rem
- sm: 0.5rem
- md: 1rem
- lg: 1.5rem
- xl: 2rem
- 2xl: 3rem

### Border Radius
- sm: 0.375rem
- md: 0.5rem
- lg: 0.75rem
- xl: 1rem

### Shadows
- sm: Subtle
- md: Standard
- lg: Prominent
- xl: Heavy

---

## Component Examples

### Button
```html
<a href="#" class="btn btn-primary">Primary Button</a>
<a href="#" class="btn btn-secondary">Secondary Button</a>
<a href="#" class="btn btn-outline-primary">Outline Button</a>
```

### Card
```html
<div class="card">
    <div class="card-body">
        <h5 class="card-title">Card Title</h5>
        <p class="card-text">Card content</p>
    </div>
</div>
```

### Alert
```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-danger">Error message</div>
```

### Form
```html
<form>
    <div class="mb-3">
        <label class="form-label">Email</label>
        <input type="email" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### Stats Box
```html
<div class="stats-box">
    <div class="stats-number">123</div>
    <div class="stats-label">Total Items</div>
</div>
```

---

## Animation Support

The template includes **AOS (Animate On Scroll)** for smooth animations:

```html
<!-- Fade up animation -->
<div data-aos="fade-up">Content</div>

<!-- Fade down animation -->
<div data-aos="fade-down">Content</div>

<!-- Slide from left -->
<div data-aos="slide-left">Content</div>

<!-- With delay -->
<div data-aos="fade-up" data-aos-delay="200">Content</div>
```

---

## Dark Mode Support

To enable dark mode, add to body:
```html
<html data-theme="dark">
```

All CSS variables automatically adapt:
- Background colors invert
- Text colors adjust
- Accents remain visible

---

## Mobile Responsiveness

Template is mobile-first with breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

All components adapt automatically.

---

## Next Steps

1. ✅ Replace base.html with base_new.html
2. ✅ Update home view to use home_new.html
3. ✅ Create public pages (about, services, contact)
4. ✅ Update all app templates to extend base_new.html
5. ✅ Copy template assets (images, icons)
6. ✅ Test responsive design
7. ✅ Customize colors/fonts for branding
8. ✅ Add custom CSS as needed

---

## Troubleshooting

### Issue: Navbar not showing properly
**Solution**: Clear browser cache and hard refresh (Ctrl+F5)

### Issue: Styles not loading
**Solution**: 
```bash
python manage.py collectstatic
```

### Issue: Animations not working
**Solution**: Ensure jQuery/Bootstrap JS is loaded from CDN

### Issue: Responsive design broken
**Solution**: Check viewport meta tag in base.html:
```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

---

## Customization Guide

### Change Primary Color
Edit `base_new.html`:
```css
--primary: #YOUR_COLOR;
--primary-dark: #YOUR_COLOR_DARK;
```

### Add Custom Font
```html
<link href="https://fonts.googleapis.com/css2?family=Your+Font:wght@300..700&display=swap" rel="stylesheet">
```

### Modify Button Styles
```css
.btn {
    border-radius: var(--radius-custom);
    padding: 0.5rem 1.25rem;
}
```

### Add Custom Gradients
```css
.custom-gradient {
    background: linear-gradient(135deg, #color1 0%, #color2 100%);
}
```

---

## Performance Tips

1. **Lazy Load Images**: Use `loading="lazy"` attribute
2. **Optimize Assets**: Compress images before uploading
3. **Minimize CSS**: Remove unused classes
4. **Cache Static Files**: Configure Django cache
5. **CDN Integration**: Use CDN for Bootstrap/jQuery

---

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

---

## Additional Resources

- Bootstrap 5 Docs: https://getbootstrap.com/docs/5.3/
- AOS Library: https://michalsnik.github.io/aos/
- Bootstrap Icons: https://icons.getbootstrap.com/
- CSS Variables: https://developer.mozilla.org/en-US/docs/Web/CSS/--*

---

## Support & Questions

For issues or customization help, refer to:
1. TEMPLATE_INTEGRATION_PLAN.md
2. Django Documentation
3. Bootstrap 5 Documentation
4. App-specific README files

