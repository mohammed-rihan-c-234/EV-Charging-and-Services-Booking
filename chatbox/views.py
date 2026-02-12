from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatSession, ChatMessage
from .forms import NewChatMessageForm, NewChatSessionForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def _service_center_id_for_user(user):
    try:
        return user.profile.service_center_id  # type: ignore[attr-defined]
    except Exception:
        return None


@login_required
def chats(request):
    """List chat sessions for the current user or service center."""
    center_id = _service_center_id_for_user(request.user)
    is_center_user = bool(center_id)
    if is_center_user:
        sessions = ChatSession.objects.select_related("user", "service_center").filter(service_center_id=center_id)
    else:
        sessions = ChatSession.objects.select_related("user", "service_center").filter(user=request.user)
    sessions = sessions.order_by("-created_at")[:50]
    return render(request, 'chatbox/chat_list.html', {'sessions': sessions, "is_center_user": is_center_user})


@login_required
def chat_create(request):
    """Create a new chat session for a selected service center."""
    if _service_center_id_for_user(request.user):
        return redirect("chatbox:list")
    if request.method == 'POST':
        form = NewChatSessionForm(request.POST)
        if form.is_valid():
            session = ChatSession.objects.create(
                user=request.user,
                service_center=form.cleaned_data["service_center"],
            )
            ChatMessage.objects.create(session=session, is_user=True, text=form.cleaned_data['message'])
            return redirect('chatbox:detail', pk=session.pk)
    else:
        form = NewChatSessionForm()
    return render(request, 'chatbox/chat_create.html', {'form': form})


@login_required
def chat_detail(request, pk):
    """Show a chat session and allow user/service-center to post messages."""
    session = get_object_or_404(ChatSession.objects.select_related("user", "service_center"), pk=pk)
    center_id = _service_center_id_for_user(request.user)
    is_center_user = bool(center_id)
    if is_center_user:
        if not session.service_center_id or session.service_center_id != center_id:
            return HttpResponseForbidden("You cannot access this chat session.")
    elif not session.user_id or session.user_id != request.user.id:
        return HttpResponseForbidden("You cannot access this chat session.")

    if request.method == 'POST':
        form = NewChatMessageForm(request.POST)
        if form.is_valid():
            ChatMessage.objects.create(
                session=session,
                is_user=not is_center_user,
                text=form.cleaned_data['message'],
            )
            return redirect('chatbox:detail', pk=pk)
    else:
        form = NewChatMessageForm()

    messages = session.messages.order_by('created_at')
    return render(
        request,
        'chatbox/chat_detail.html',
        {
            'session': session,
            'messages': messages,
            'form': form,
            'is_center_user': is_center_user,
        },
    )
