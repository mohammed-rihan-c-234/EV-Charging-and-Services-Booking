# Template Integration Quick Reference

## File Structure
```
ev_project_django/
├── templates/
│   ├── base_new.html (Modern base template)
│   ├── home_new.html (Modern homepage)
│   ├── includes/
│   │   ├── hero_section.html
│   │   ├── section_title.html
│   │   ├── feature_card.html
│   │   ├── stats_box.html
│   │   └── card.html
│   └── public/
│       ├── about.html
│       └── contact.html
├── static/
│   └── css/
│       └── template.css (Custom styles)
├── TEMPLATE_INTEGRATION_PLAN.md (Strategy guide)
└── IMPLEMENTATION_GUIDE.md (Setup guide)
```

## Quick Setup
1. Update urls.py to use new templates
2. Replace base.html with base_new.html
3. Update home view to render home_new.html
4. Test the homepage

## Modern Design Features
- ✅ Responsive grid layout
- ✅ Smooth animations (AOS library)
- ✅ Gradient backgrounds
- ✅ Card-based design system
- ✅ Dark mode support
- ✅ Mobile-first approach
- ✅ Bootstrap 5 integration
- ✅ Professional spacing and typography

## Key CSS Classes

### Colors
- `text-primary` - Blue text
- `text-gradient` - Gradient text effect
- `bg-gradient-primary` - Gradient background

### Components
- `.card` - Styled card container
- `.btn` - Button with animations
- `.hero` - Large hero section
- `.stats-box` - Statistics display
- `.alert` - Alert messages
- `.service-card` - Service showcase
- `.feature-box` - Feature highlight

### Animations
- `data-aos="fade-up"` - Fade in from bottom
- `data-aos="fade-down"` - Fade in from top
- `data-aos="fade-left"` - Fade in from left
- `data-aos="fade-right"` - Fade in from right
- `data-aos-delay="100"` - Animation delay

### Utilities
- `.section-padding` - Standard section spacing
- `.container-lg` - Max-width container
- `.hover-lift` - Lift on hover effect
- `.hover-scale` - Scale on hover effect

## Color Palette
- Primary: `#2563eb` (Blue)
- Secondary: `#7c3aed` (Purple)
- Accent: `#ec4899` (Pink)
- Success: `#10b981` (Green)
- Warning: `#f59e0b` (Amber)
- Danger: `#ef4444` (Red)

## Typography
- Headings: Plus Jakarta Sans (bold)
- Body: Inter (regular)
- Code: Monospace font

## Responsive Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## Form Elements
```html
<div class="mb-3">
    <label class="form-label">Label</label>
    <input type="text" class="form-control" required>
</div>
```

## Buttons
```html
<a href="#" class="btn btn-primary">Primary</a>
<a href="#" class="btn btn-secondary">Secondary</a>
<a href="#" class="btn btn-outline-primary">Outline</a>
```

## Cards
```html
<div class="card">
    <div class="card-body">
        <h5 class="card-title">Title</h5>
        <p class="card-text">Content</p>
    </div>
</div>
```

## Hero Section
```html
<section class="hero">
    <div class="container-lg">
        <h1>Title</h1>
        <p>Subtitle</p>
    </div>
</section>
```

## Alerts
```html
<div class="alert alert-success">Success!</div>
<div class="alert alert-danger">Error!</div>
<div class="alert alert-warning">Warning!</div>
```

## Common Patterns

### Feature Grid
```html
<div class="row g-4">
    {% for feature in features %}
    <div class="col-lg-4 col-md-6" data-aos="fade-up">
        <div class="card">
            <!-- content -->
        </div>
    </div>
    {% endfor %}
</div>
```

### Stats Section
```html
<div class="row">
    <div class="col-md-3">
        <div class="stats-box">
            <div class="stats-number">100</div>
            <div class="stats-label">Users</div>
        </div>
    </div>
</div>
```

### Service Cards
```html
<div class="service-card">
    <div class="service-card-icon" style="background: var(--gradient-primary); color: white;">
        <i class="bi bi-icon"></i>
    </div>
    <h6>Title</h6>
    <p class="text-muted">Description</p>
</div>
```

## Navigation Links
```html
<a href="/dashboard/">Dashboard</a>
<a href="/vehicles/">Vehicles</a>
<a href="/charging/">Charging</a>
<a href="/sos/">Emergency SOS</a>
<a href="/services/">Services</a>
<a href="/chatbox/">Support Chat</a>
<a href="/spareparts/">Spare Parts</a>
<a href="/rewards/">Rewards</a>
```

## Common Icons (Bootstrap Icons)
- `bi-lightning-charge` - EV/Energy
- `bi-telephone-outbound` - Emergency/Call
- `bi-tools` - Service/Maintenance
- `bi-gear` - Settings/Parts
- `bi-chat-dots` - Chat/Support
- `bi-star` - Rewards/Rating
- `bi-ev-front` - EV Vehicle
- `bi-map-fill` - Location/Maps
- `bi-calendar-event` - Booking/Schedule

## Dark Mode
Add to html tag:
```html
<html data-theme="dark">
```

## Performance Tips
- Use `loading="lazy"` for images
- Minimize CSS classes
- Cache static files
- Optimize images

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## Troubleshooting

### Navbar not sticky
Check CSS: `.navbar { position: fixed; }`

### Animations not working
Verify AOS library is loaded from CDN

### Styling not applied
Clear cache: `python manage.py collectstatic`

### Responsive layout broken
Check viewport meta tag in base.html

## Next Steps
1. Customize colors for your brand
2. Add custom fonts if needed
3. Optimize images for web
4. Configure CDN for assets
5. Test across devices
6. Set up analytics

## Resources
- [Bootstrap 5 Documentation](https://getbootstrap.com/)
- [AOS Animation Library](https://michalsnik.github.io/aos/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)
- [MDN Web Docs](https://developer.mozilla.org/)

## Support
Check IMPLEMENTATION_GUIDE.md for detailed setup instructions.
