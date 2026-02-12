from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatSession, ChatMessage
from .forms import NewChatMessageForm


def chats(request):
    """List recent chat sessions and provide a link to create a new one."""
    sessions = ChatSession.objects.order_by('-created_at')[:50]
    return render(request, 'chatbox/chat_list.html', {'sessions': sessions})


def chat_create(request):
    """Create a new chat session and optionally add the first message."""
    if request.method == 'POST':
        form = NewChatMessageForm(request.POST)
        if form.is_valid():
            # create session; if user not logged in, create anonymous session without user
            session = ChatSession.objects.create(user=request.user if request.user.is_authenticated else None)
            ChatMessage.objects.create(session=session, is_user=True, text=form.cleaned_data['message'])
            return redirect('chatbox:detail', pk=session.pk)
    else:
        form = NewChatMessageForm()
    return render(request, 'chatbox/chat_create.html', {'form': form})


def chat_detail(request, pk):
    """Show a chat session and allow posting new messages."""
    session = get_object_or_404(ChatSession, pk=pk)
    if request.method == 'POST':
        form = NewChatMessageForm(request.POST)
        if form.is_valid():
            ChatMessage.objects.create(session=session, is_user=True, text=form.cleaned_data['message'])
            return redirect('chatbox:detail', pk=pk)
    else:
        form = NewChatMessageForm()

    messages = session.messages.order_by('created_at')
    return render(request, 'chatbox/chat_detail.html', {'session': session, 'messages': messages, 'form': form})
