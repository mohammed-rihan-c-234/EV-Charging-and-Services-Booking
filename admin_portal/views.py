from django.apps import apps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q
from django.forms import modelform_factory
from django.http import Http404
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render


def _is_staff(user):
    return bool(user and user.is_authenticated and user.is_staff)


def _perm_name(meta, action):
    return f"{meta.app_label}.{action}_{meta.model_name}"


def _portal_model_entries(user):
    entries = []
    excluded_apps = {"admin_portal"}
    for app_config in apps.get_app_configs():
        if app_config.label in excluded_apps:
            continue
        for model in app_config.get_models():
            meta = model._meta
            if meta.auto_created or meta.proxy or not meta.managed:
                continue
            perms = {
                "view": user.has_perm(_perm_name(meta, "view")) or user.has_perm(_perm_name(meta, "change")),
                "add": user.has_perm(_perm_name(meta, "add")),
                "change": user.has_perm(_perm_name(meta, "change")),
                "delete": user.has_perm(_perm_name(meta, "delete")),
            }
            if not any(perms.values()):
                continue
            entries.append(
                {
                    "app_label": meta.app_label,
                    "model_name": meta.model_name,
                    "verbose_name": meta.verbose_name.title(),
                    "verbose_name_plural": meta.verbose_name_plural.title(),
                    "model": model,
                    "perms": perms,
                }
            )
    entries.sort(key=lambda x: (x["app_label"], x["verbose_name_plural"]))
    return entries


def _get_model_or_404(app_label, model_name):
    model = apps.get_model(app_label, model_name)
    if model is None:
        raise Http404("Model not found")
    meta = model._meta
    if meta.auto_created or meta.proxy or not meta.managed:
        raise Http404("Model not available")
    return model


def _base_context(user):
    entries = _portal_model_entries(user)
    return {"portal_models": entries}


@login_required
@user_passes_test(_is_staff)
def dashboard(request):
    entries = _portal_model_entries(request.user)
    cards = []
    total_rows = 0
    for entry in entries:
        count = entry["model"].objects.count()
        total_rows += count
        cards.append(
            {
                "app_label": entry["app_label"],
                "model_name": entry["model_name"],
                "name": entry["verbose_name_plural"],
                "count": count,
                "perms": entry["perms"],
            }
        )
    context = _base_context(request.user)
    context.update(
        {
            "cards": cards,
            "total_models": len(cards),
            "total_rows": total_rows,
            "active_key": "",
        }
    )
    return render(request, "admin_portal/dashboard.html", context)


@login_required
@user_passes_test(_is_staff)
def model_list(request, app_label, model_name):
    model = _get_model_or_404(app_label, model_name)
    meta = model._meta
    can_view = request.user.has_perm(_perm_name(meta, "view")) or request.user.has_perm(_perm_name(meta, "change"))
    can_add = request.user.has_perm(_perm_name(meta, "add"))
    can_change = request.user.has_perm(_perm_name(meta, "change"))
    can_delete = request.user.has_perm(_perm_name(meta, "delete"))
    if not can_view:
        return HttpResponseForbidden("You do not have permission to view this model.")
    qs = model.objects.all().order_by("-pk")

    q = (request.GET.get("q") or "").strip()
    search_fields = [f.name for f in meta.fields if isinstance(f, (models.CharField, models.TextField))]
    if q:
        query = Q()
        for field_name in search_fields:
            query |= Q(**{f"{field_name}__icontains": q})
        if q.isdigit():
            query |= Q(pk=int(q))
        qs = qs.filter(query)

    columns = [meta.pk]
    concrete_fields = [f for f in meta.fields if f.name != meta.pk.name]
    columns.extend(concrete_fields[:5])

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get("page"))
    rows = []
    for obj in page_obj.object_list:
        values = []
        for field in columns:
            value = getattr(obj, field.name, "")
            values.append("" if value is None else str(value))
        rows.append({"pk": obj.pk, "values": values})

    context = _base_context(request.user)
    context.update(
        {
            "model": model,
            "meta": meta,
            "columns": columns,
            "rows": rows,
            "page_obj": page_obj,
            "q": q,
            "can_add": can_add,
            "can_change": can_change,
            "can_delete": can_delete,
            "active_key": f"{app_label}.{model_name}",
        }
    )
    return render(request, "admin_portal/model_list.html", context)


def _model_form_view(request, app_label, model_name, instance=None):
    model = _get_model_or_404(app_label, model_name)
    meta = model._meta
    if instance is None:
        if not request.user.has_perm(_perm_name(meta, "add")):
            return HttpResponseForbidden("You do not have permission to add this model.")
    else:
        if not request.user.has_perm(_perm_name(meta, "change")):
            return HttpResponseForbidden("You do not have permission to edit this model.")
    form_class = modelform_factory(model, fields="__all__")
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("admin_portal:model_list", app_label=app_label, model_name=model_name)
    else:
        form = form_class(instance=instance)
    for field in form.fields.values():
        if "class" not in field.widget.attrs:
            field.widget.attrs["class"] = "form-control"
    context = _base_context(request.user)
    context.update(
        {
            "form": form,
            "meta": meta,
            "is_edit": instance is not None,
            "active_key": f"{app_label}.{model_name}",
        }
    )
    return render(request, "admin_portal/model_form.html", context)


@login_required
@user_passes_test(_is_staff)
def model_create(request, app_label, model_name):
    return _model_form_view(request, app_label, model_name, instance=None)


@login_required
@user_passes_test(_is_staff)
def model_edit(request, app_label, model_name, pk):
    model = _get_model_or_404(app_label, model_name)
    instance = get_object_or_404(model, pk=pk)
    return _model_form_view(request, app_label, model_name, instance=instance)


@login_required
@user_passes_test(_is_staff)
def model_delete(request, app_label, model_name, pk):
    model = _get_model_or_404(app_label, model_name)
    meta = model._meta
    if not request.user.has_perm(_perm_name(meta, "delete")):
        return HttpResponseForbidden("You do not have permission to delete this model.")
    instance = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        instance.delete()
        return redirect("admin_portal:model_list", app_label=app_label, model_name=model_name)
    context = _base_context(request.user)
    context.update(
        {
            "meta": meta,
            "instance": instance,
            "active_key": f"{app_label}.{model_name}",
        }
    )
    return render(request, "admin_portal/model_delete.html", context)
