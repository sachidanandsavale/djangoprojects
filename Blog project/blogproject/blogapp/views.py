from django.shortcuts import render,get_object_or_404
from blogapp.models import Post
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from blogapp.models import *
from blogapp.forms import *
from taggit.models import Tag
# Create your views here.

def post_list_view(request,tag_slug=None):
	post_list=Post.objects.all()
	tag=None
	if tag_slug:
		tag=get_object_or_404(Tag,slug=tag_slug)
		post_list=post_list.filter(tags__in=[tag])

	paginator=Paginator(post_list, 2)
	page_number=request.GET.get('page')

	try:
		post_list=paginator.page(page_number)

	except PageNotAnInteger:
		post_list=paginator.page(1)

	except EmptyPage:
		post_list=Paginator.page(paginator.num_pages)

	my_dict={'post_list':post_list,'tag':tag}
	return render(request=request, template_name='blogapp/post_list.html',context=my_dict)

#class based view for Pagination
from django.views.generic import ListView
class PostListView(ListView):
	model=Post
	paginate_by=2

def post_detail_view(request,year,month,day,post):
	post = get_object_or_404(Post,slug=post,status='published',publish__year=year,publish__month=month,publish__day=day)
	comments=post.comments.filter(active=True)
	csubmit=False
	if request.method=='POST':
		form=CommentForm(request.POST)
		if form.is_valid():
			new_comment=form.save(commit=False)
			new_comment.post=post 
			new_comment.save()
			csubmit=True

	else:
		form=CommentForm()

	my_dict={'post':post,'form':form,'csubmit':csubmit,'comments':comments}
	return render(request=request, template_name='blogapp/post_detail.html',context=my_dict)


from blogapp.forms import EmailSendForm
from django.core.mail import send_mail

def mail_send_view(request,id):
	post=get_object_or_404(Post,id=id,status='published')
	sent=False
	if request.method=='POST':
		form=EmailSendForm(request.POST)
		if form.is_valid():
			cd=form.cleaned_data
			subject='{}({}) recommends you to read"{}" '.format(cd['name'],cd['email'],post.title)
			
			post_url=request.build_absolute_uri(post.get_absolute_url())
			message='Read the Post at :\n {} \n\n {}\'s Comments:\n{}'.format(post_url,cd['name'],cd['comments'])
			send_mail(subject, message, 'sandesh@blog.com',[cd['to']])
			sent=True 

	else:
		form=EmailSendForm()

	my_dict={'form':form,'post':post,'sent':sent}
	return render(request=request, template_name='blogapp/sharebymail.html',context=my_dict)