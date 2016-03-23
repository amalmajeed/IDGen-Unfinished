from django.shortcuts import render, get_object_or_404
from .forms import StudentForm,FacultyForm,Sd, Fd,SingleStud
from .models import stud,faculty,SDesign, FDesign
import re
from django.http import HttpResponse,HttpResponseRedirect
# imports for reportlab pdfgeneration 
import os
import urllib2
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from django.utils.encoding import smart_str
from django.core.exceptions import ObjectDoesNotExist
#from django.core.exceptions import DoesNotExist
import zipfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def login1(request):
  next=request.GET.get('next','/idcard/')
  if request.method=="POST":
    username=request.POST['username']
    password=request.POST['password']
    user=authenticate(username=username,password=password)
    if user is not None:
      if user.is_active:
        login(request,user)
        return HttpResponseRedirect('/idcard/')
      else:
        HttpResponse("Inactive user!")
    else:
      return HttpResponseRedirect('/idcard/login/')
  return render(request,"upload/login.html",{'redirect_to':next})


def logout1(request):
  logout(request)
  return HttpResponseRedirect('/idcard/login/')


@login_required(login_url='/idcard/login/')
def mainpage(request):
   return render(request,'upload/home.html')

@login_required(login_url='/idcard/login/')
def mainstu(request):
   return render(request,'upload/homestu.html')

@login_required(login_url='/idcard/login/')
def mainfac(request):
   return render(request,'upload/homefac.html')

@login_required(login_url='/idcard/login/')
def student(request):
   if request.method=='POST':
     try:
      a=stud.objects.get(admno=request.POST.get("admno"))
     except:
      form=StudentForm(request.POST,request.FILES)
      if form.is_valid():
        instance=form.save(commit=False)
        instance.save()
        return render(request,'upload/home.html') 
      else:
         errormsg="Form not valid"
         form=StudentForm()
         context={"form":form,"error_message":errormsg}
         return render(request,'upload/studentform.html',context)
     errormsg="Student Exists"
     form=StudentForm()
     context={"form":form,"error_message":errormsg}
     return render(request,'upload/studentform.html',context)
   else:
    form=StudentForm()
    context={"form":form}
    return render(request,'upload/studentform.html',context)

@login_required(login_url='/idcard/login/')
def faculty1(request):
   if request.method=='POST':
    try:
      a=faculty.objects.get(name=request.POST.get("name"))
    except:
     form=FacultyForm(request.POST,request.FILES)
     if form.is_valid():
       instance=form.save(commit=False)
       instance.save()
       return render(request,'upload/home.html') 
     else:
       errormsg="Form not valid"
       form=FacultyForm()
       context={"form":form,"error_message":errormsg}
       return render(request,'upload/facultyform.html',context)
    errormsg="Faculty Exists"
    form=FacultyForm()
    context={"form":form,"error_message":errormsg}
    return render(request,'upload/facultyform.html',context)
   else:
     #errormsg="Method not POST"
     form=FacultyForm()
     context={"form":form}
     return render(request,'upload/facultyform.html',context)


@login_required(login_url='/idcard/login/')
def studentDetailedEdit(request, id=None):
  q = get_object_or_404(stud, id=id)
  return render(request,'upload/studeditform.html',{'i':q})

@login_required(login_url='/idcard/login/')
def facultyEdit(request, id=None):
  q = get_object_or_404(faculty, id=id)
  return render(request,'upload/faceditform.html',{'i':q})

@login_required(login_url='/idcard/login/')
def studentpdfhome(request):
	return render(request,'upload/genpdf.html')

@login_required(login_url='/idcard/login/')
def generatepdf(request):
	if request.method=="POST":
		try:
			smallest=100000000
			largest=0
			for i in stud.objects.all():
			    a=int(i.admno.split('/')[0])
			    if a<smallest:
			    	smallest=a
			    	#print smallest
			    elif a>largest:
		      		largest=a
		      		#print largest
			a=int(request.POST['range'].split('-')[0])
			b=int(request.POST['range'].split('-')[1])
			q=[]
			if(a<smallest):
				a=smallest
				#print smallest
			elif(b>largest):
				b=largest
				#print largest
			for i in stud.objects.all():
				if((int(i.admno.split('/')[0])>=smallest)and(int(i.admno.split('/')[0])<=largest)):
					q.append(i)

			if q.__len__()==0:
				print "NOW WERE HERE"
			  	return render(request,'upload/home.html')
			details=SDesign.objects.get()
			back = root +'/'+str(details.bdesign)[2:]
			princi = root + '/'+str(details.psign)[2:]
			logoright = root+'/'+ str(details.ilogo)[2:]
			logoleft = root +'/'+ str(details.clogo)[2:]
			width = 540*mm
			height = 860*mm
			c = canvas.Canvas('rangefront.pdf')
			for i in q:
			  pic =i.photo.url
			  c.setPageSize((width, height))
			  if back:
			    c.drawImage(back, 0, 0, height=height, width=width)
			#c.saveState()
			  if logoleft:
			    c.drawImage(logoleft, 20*mm, 740*mm, height=80*mm, width=80*mm)
			  if logoright:
			    c.drawImage(logoright, 450*mm, 740*mm, height=80*mm, width=80*mm)
			  c.setFont(str(details.cfont), int(details.cfontsize))
			  c.drawCentredString(width/2, height-(60*mm),str(details.college))
			  c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
			  c.drawCentredString(width/2, height-(80*mm),str(details.addline1))
			  c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
			  c.drawCentredString(width/2, height-(100*mm), str(details.addline2))
			  #c.drawCentredString(width/2, height-(120*mm), "")  Kerala, India, PIN: 682 021 
			  c.drawCentredString(width/2, height-(120*mm),str(details.addline3))
			  c.drawCentredString(width/2, height-(140*mm),str(details.addline4))
			  c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
			  c.drawCentredString(width/2, height-(160*mm), str(details.addline5))
			  c.drawImage(pic, 170*mm, height-(375*mm), height=200*mm, width=200*mm)
			  c.setFont(str(details.detfont), int(details.detfontsize))
			  c.drawString(30*mm, 430*mm, "Name ")
			  c.drawString(165*mm, 430*mm,i.name)
			  c.setFont(str(details.detfont), int(details.detfontsize))
			  c.drawString(30*mm, 340*mm, "Course :")
			  c.drawString(165*mm, 340*mm,i.course)
			  c.drawString(30*mm, 280*mm, "Branch :")
			  c.drawString(165*mm, 280*mm, i.branch)
			  c.drawString(30*mm, 180*mm, "ADMN No :")
			  c.drawString(165*mm, 180*mm, i.admno)
			  c.drawString(30*mm, 120*mm, "Valid Till:")
			  c.drawString(165*mm, 120*mm,str(i.validtill.day)+'/'+str(i.validtill.month)+'/'+str(i.validtill.year))
			  c.drawString(30*mm, 60*mm, "Date Of Birth:")
			  c.drawString(165*mm, 60*mm,str(i.dateofbirth.day)+'/'+str(i.dateofbirth.month)+'/'+str(i.dateofbirth.year))
			  c.setFont('Times-Bold', 60)
			  c.drawString(420*mm, 20*mm, "Principal")
			  if princi:
			    c.drawImage(princi, 420*mm, 45*mm, height= 50*mm, width=80*mm)
			  c.showPage()
			c.save()
			c = canvas.Canvas('rangeback.pdf')
			for i in q:
			  barcode_value = ""
			  if(i.course[0]=="B"):
			    barcode_value+="U"
			  else:
			    barcode_value+="P"
			  barcode_value+=i.admno.split('/')[0]+i.admno.split('/')[1]
			  barcode_value+=str(i.clss)
			  barcode_value+=str(i.rollno)
			  barcode128 = code128.Code128(barcode_value, barHeight=50*mm, barWidth=1.5*mm)
			  c.setPageSize((width, height))
			  c.setFont(str(details.detfont), int(details.detfontsize))
			  barcode128.drawOn(c, 130*mm, 750*mm)
			  c.drawString(190*mm, 720*mm, barcode_value)
			  c.drawString(30*mm, 630*mm, "Blood Group ")
			  c.drawString(210*mm, 630*mm,i.bloodgroup)
			  c.drawString(30*mm, 550*mm, "Address ")
			  le=i.address.__len__()
			  n=0
			      #x=2
			  ht=550
			  y=re.split(',',i.address)
			  y=re.split(',',i.address)
			  for x in y:
			    c.drawString(210*mm, ht*mm,x)
			    ht=ht-40
			  #c.drawString(210*mm, 550*mm, ": FLAT 2A")
			  #c.drawString(210*mm, 500*mm, "  SLYLINE BUILDERS")
			  #c.drawString(210*mm, 450*mm, "  APJ ROAD")
			  #c.drawString(210*mm, 400*mm, "  EDAPPALLY TOLL,")
			  #c.drawString(210*mm, 350*mm, "  EDAPPALLY P.O.")
			  #c.drawString(210*mm, 300*mm, "  682024")
			  c.drawString(30*mm, 170*mm, "Contact No. ")
			  c.drawString(210*mm, 170*mm,i.contact1)
			  c.drawString(210*mm, 140*mm,i.contact2)
			  c.drawString(30*mm, 60*mm, "Signature     :")
			  c.rect(160*mm,30*mm,320*mm,70*mm)
			  c.showPage()
			c.save()
			     ###### TO DISPLAY PDF VIA BROWSER  ###
			     #with open('amal.pdf', 'rb') as pdf:
			     #   response = HttpResponse(pdf.read(),content_type='application/pdf')
			     #   response['Content-Disposition'] = 'filename=some_file.pdf'
			     #   return response
			     #pdf.closed
			arch=zipfile.ZipFile("range.zip","w")
			arch.write('rangefront.pdf')
			arch.write('rangeback.pdf')
			arch.close()
			response = HttpResponse(open(root+'/range.zip', 'rb').read(), content_type='application/zip')
			response['Content-Disposition'] = 'attachment; filename=range.zip'
			return response
			return render(request,'upload/home.html')				
		except:
		    return HttpResponseRedirect('/idcard/')
	else:
	  q=stud.objects.all()
	  if q.__len__()==0:
	  	return render(request,'upload/home.html')
	  details=SDesign.objects.get()
	  back = root +'/'+str(details.bdesign)[2:]
	  princi = root + '/'+str(details.psign)[2:]
	  logoright = root+'/'+ str(details.ilogo)[2:]
	  logoleft = root +'/'+ str(details.clogo)[2:]
	  width = 540*mm
	  height = 860*mm
	  c = canvas.Canvas('front.pdf')
	  for i in q:
	    pic =i.photo.url
	    c.setPageSize((width, height))
	    if back:
	      c.drawImage(back, 0, 0, height=height, width=width)
	  #c.saveState()
	    if logoleft:
	      c.drawImage(logoleft, 20*mm, 740*mm, height=80*mm, width=80*mm)
	    if logoright:
	      c.drawImage(logoright, 450*mm, 740*mm, height=80*mm, width=80*mm)
	    c.setFont(str(details.cfont), int(details.cfontsize))
	    c.drawCentredString(width/2, height-(60*mm),str(details.college))
	    c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
	    c.drawCentredString(width/2, height-(80*mm),str(details.addline1))
	    c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
	    c.drawCentredString(width/2, height-(100*mm), str(details.addline2))
	    #c.drawCentredString(width/2, height-(120*mm), "")  Kerala, India, PIN: 682 021 
	    c.drawCentredString(width/2, height-(120*mm),str(details.addline3))
	    c.drawCentredString(width/2, height-(140*mm),str(details.addline4))
	    c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
	    c.drawCentredString(width/2, height-(160*mm), str(details.addline5))
	    c.drawImage(pic, 170*mm, height-(375*mm), height=200*mm, width=200*mm)
	    c.setFont(str(details.detfont), int(details.detfontsize))
	    c.drawString(30*mm, 430*mm, "Name ")
	    c.drawString(165*mm, 430*mm,i.name)
	    c.setFont(str(details.detfont), int(details.detfontsize))
	    c.drawString(30*mm, 340*mm, "Course :")
	    c.drawString(165*mm, 340*mm,i.course)
	    c.drawString(30*mm, 280*mm, "Branch :")
	    c.drawString(165*mm, 280*mm, i.branch)
	    c.drawString(30*mm, 180*mm, "ADMN No :")
	    c.drawString(165*mm, 180*mm, i.admno)
	    c.drawString(30*mm, 120*mm, "Valid Till:")
	    c.drawString(165*mm, 120*mm,str(i.validtill.day)+'/'+str(i.validtill.month)+'/'+str(i.validtill.year))
	    c.drawString(30*mm, 60*mm, "Date Of Birth:")
	    c.drawString(165*mm, 60*mm,str(i.dateofbirth.day)+'/'+str(i.dateofbirth.month)+'/'+str(i.dateofbirth.year))
	    c.setFont('Times-Bold', 60)
	    c.drawString(420*mm, 20*mm, "Principal")
	    if princi:
	      c.drawImage(princi, 420*mm, 45*mm, height= 50*mm, width=80*mm)
	    c.showPage()
	  c.save()
	  c = canvas.Canvas('back.pdf')
	  for i in q:
	    barcode_value = ""
	    if(i.course[0]=="B"):
	      barcode_value+="U"
	    else:
	      barcode_value+="P"
	    barcode_value+=i.admno.split('/')[0]+i.admno.split('/')[1]
	    barcode_value+=str(i.clss)
	    barcode_value+=str(i.rollno)
	    barcode128 = code128.Code128(barcode_value, barHeight=50*mm, barWidth=1.5*mm)
	    c.setPageSize((width, height))
	    c.setFont(str(details.detfont), int(details.detfontsize))
	    barcode128.drawOn(c, 130*mm, 750*mm)
	    c.drawString(190*mm, 720*mm, barcode_value)
	    c.drawString(30*mm, 630*mm, "Blood Group ")
	    c.drawString(210*mm, 630*mm,i.bloodgroup)
	    c.drawString(30*mm, 550*mm, "Address ")
	    le=i.address.__len__()
	    n=0
	        #x=2
	    ht=550
	    y=re.split(',',i.address)
	    y=re.split(',',i.address)
	    for x in y:
	      c.drawString(210*mm, ht*mm,x)
	      ht=ht-40
	    #c.drawString(210*mm, 550*mm, ": FLAT 2A")
	    #c.drawString(210*mm, 500*mm, "  SLYLINE BUILDERS")
	    #c.drawString(210*mm, 450*mm, "  APJ ROAD")
	    #c.drawString(210*mm, 400*mm, "  EDAPPALLY TOLL,")
	    #c.drawString(210*mm, 350*mm, "  EDAPPALLY P.O.")
	    #c.drawString(210*mm, 300*mm, "  682024")
	    c.drawString(30*mm, 170*mm, "Contact No. ")
	    c.drawString(210*mm, 170*mm,i.contact1)
	    c.drawString(210*mm, 140*mm,i.contact2)
	    c.drawString(30*mm, 60*mm, "Signature     :")
	    c.rect(160*mm,30*mm,320*mm,70*mm)
	    c.showPage()
	  c.save()
	       ###### TO DISPLAY PDF VIA BROWSER  ###
	       #with open('amal.pdf', 'rb') as pdf:
	       #   response = HttpResponse(pdf.read(),content_type='application/pdf')
	       #   response['Content-Disposition'] = 'filename=some_file.pdf'
	       #   return response
	       #pdf.closed
	  arch=zipfile.ZipFile("id.zip","w")
	  arch.write('front.pdf')
	  arch.write('back.pdf')
	  arch.close()
	  response = HttpResponse(open(root+'/id.zip', 'rb').read(), content_type='application/zip')
	  response['Content-Disposition'] = 'attachment; filename=simple.zip'
	  return response
	  return render(request,'upload/home.html')

@login_required(login_url='/idcard/login/')
def rlab(request):
  details = SDesign.objects.get()
        #print str(details.bdesign.url)[2:]
  back = root +'/'+str(details.bdesign)[2:]
  pic = root + '/student-sample.jpg'
  princi = root + '/'+str(details.psign)[2:]
  logoright = root+'/'+ str(details.ilogo)[2:]
  logoleft = root +'/'+ str(details.clogo)[2:]
  barcode_value = "U610013CSB28"
  barcode128 = code128.Code128(barcode_value, barHeight=50*mm, barWidth=1.5*mm)
  width = 540*mm
  height = 860*mm
        #print str(details.college)
  c = canvas.Canvas('student.pdf')
  c.setPageSize((width, height))
  if back:
    c.drawImage(back, 0, 0, height=height, width=width)
  #c.saveState()
  if logoleft:
    c.drawImage(logoleft, 20*mm, 740*mm, height=80*mm, width=80*mm)
  if logoright:
    c.drawImage(logoright, 450*mm, 740*mm, height=80*mm, width=80*mm)
  c.setFont(str(details.cfont), int(details.cfontsize))
  c.drawCentredString(width/2, height-(60*mm),str(details.college))
  c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
  c.drawCentredString(width/2, height-(80*mm),str(details.addline1))
  c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
  c.drawCentredString(width/2, height-(100*mm), str(details.addline2))
  #c.drawCentredString(width/2, height-(120*mm), "")  Kerala, India, PIN: 682 021 
  c.drawCentredString(width/2, height-(120*mm),str(details.addline3))
  c.drawCentredString(width/2, height-(140*mm),str(details.addline4))
  c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
  c.drawCentredString(width/2, height-(160*mm), str(details.addline5))
  c.drawImage(pic, 170*mm, height-(375*mm), height=200*mm, width=200*mm)
  c.setFont(str(details.detfont), int(details.detfontsize))
  c.drawString(30*mm, 430*mm, "Name ")
  c.drawString(165*mm, 430*mm, ": AMAL MAJEED")
  c.setFont(str(details.detfont), int(details.detfontsize))
  c.drawString(30*mm, 340*mm, "Course ")
  c.drawString(165*mm, 340*mm, ": BTech")
  c.drawString(30*mm, 280*mm, "Branch ")
  c.drawString(165*mm, 280*mm, ": Computer Science And Engineering")
  c.drawString(30*mm, 180*mm, "ADMN No ")
  c.drawString(165*mm, 180*mm, ": 6100/13")
  c.drawString(30*mm, 120*mm, "Valid Till ")
  c.drawString(165*mm, 120*mm, ": 30-06-2017")
  c.drawString(30*mm, 60*mm, "Date Of Birth ")
  c.drawString(165*mm, 60*mm, ": 18/04/1995")
  c.setFont('Times-Bold', 60)
  c.drawString(420*mm, 20*mm, "Principal")
  if princi:
    c.drawImage(princi, 420*mm, 45*mm, height= 50*mm, width=80*mm)
  c.showPage()

  c.setFont(str(details.detfont), int(details.detfontsize))
  barcode128.drawOn(c, 130*mm, 750*mm)
  c.drawString(190*mm, 720*mm, "U617513CSB27")
  c.drawString(30*mm, 630*mm, "Blood Group ")
  c.drawString(210*mm, 630*mm, ": B+")
  c.drawString(30*mm, 550*mm, "Address ")
  c.drawString(210*mm, 550*mm, ": FLAT 2A")
  c.drawString(210*mm, 500*mm, "  SLYLINE BUILDERS")
  c.drawString(210*mm, 450*mm, "  APJ ROAD")
  c.drawString(210*mm, 400*mm, "  EDAPPALLY TOLL,")
  c.drawString(210*mm, 350*mm, "  EDAPPALLY P.O.")
  c.drawString(210*mm, 300*mm, "  682024")
  c.drawString(30*mm, 170*mm, "Contact No. ")
  c.drawString(210*mm, 170*mm, ": 0484-2577539")
  c.drawString(210*mm, 140*mm, "  8891696434")
  c.drawString(30*mm, 60*mm, "Signature     :")
  c.rect(160*mm,30*mm,320*mm,70*mm)
  
  c.save()

  with open('student.pdf', 'rb') as pdf:
    response = HttpResponse(pdf.read(),content_type='application/pdf')
    response['Content-Disposition'] = 'filename=some_file.pdf'
    return response
  pdf.closed

@login_required(login_url='/idcard/login/')
def editstud(request):
	if request.method=='POST':
		if request.POST.get('selection') is None:
			for i in stud.objects.all():
				i.clss=request.POST['clss'+str(i.pk)]
				i.branch=request.POST['branch'+str(i.pk)]
				i.rollno=request.POST['rollno'+str(i.pk)]
				i.save()
			return render(request,'upload/home.html')
		else:
			q=stud.objects.get(admno=request.POST['selection'])
			return render(request,'upload/studeditform.html',{'i':q})
	else:
		return render(request,'upload/home.html')         
   
@login_required(login_url='/idcard/login/')
def editfac(request):
   if request.method=='POST':
	  if request.POST.get('selection') is None:
	  	return render(request,'upload/home.html')
	  else:
	    q=faculty.objects.get(name=request.POST['selection'])
	    return render(request,'upload/faceditform.html',{'q':q}) 	
      
@login_required(login_url='/aidcard/login/')
def studsave(request):
   if request.method=='POST':
	   q=stud.objects.get(pk=request.POST['stu'])
	   q.name=request.POST.get('name'+str(q.pk))
	   q.course=request.POST.get('course'+str(q.pk))
	   q.branch=request.POST.get('branch'+str(q.pk))
	   q.admno=request.POST.get('admno'+str(q.pk))
	   q.validtill=request.POST.get('validtill'+str(q.pk))
	   q.dateofbirth=request.POST.get('dateofbirth'+str(q.pk))
	   q.bloodgroup=request.POST.get('bloodgroup'+str(q.pk))
	   q.address=request.POST.get('address'+str(q.pk))
	   q.contact1=request.POST.get('contact1'+str(q.pk))
	   q.contact2=request.POST.get('contact2'+str(q.pk))  
	   q.clss=request.POST.get('clss'+str(q.pk))
	   q.rollno=request.POST.get('rollno'+str(q.pk))
	   if(request.FILES.get('photo'+str(q.pk))):
	       os.system('rm '+q.photo.url)
	       q.photo=request.FILES.get('photo'+str(q.pk))
	   q.save()
	   return render(request,'upload/liststud.html',{'students':stud.objects.all()})
   else:
	   return render(request,'upload/home.html')
   
@login_required(login_url='/idcard/login/')
def facsave(request):
   if request.method=='POST':
       q=faculty.objects.get(pk=request.POST['fac'])
       q.name=request.POST.get('name')
       q.designation=request.POST.get('designation')
       q.dateofbirth=request.POST.get('dateofbirth')
       q.bloodgroup=request.POST.get('bloodgroup')
       q.address=request.POST.get('address')
       q.contact=request.POST.get('contact')
       if(request.FILES.get('photo')):
           os.system('rm '+q.photo.url)
           q.photo=request.FILES.get('photo')
       q.save()
       return render(request,'upload/listfac.html',{'faculty':faculty.objects.all()})
   else:
	   return render(request,'upload/home.html')
   
@login_required(login_url='/idcard/login/')
def delstud(request):
   if request.method=='POST':
      try:
         q=stud.objects.get(admno=request.POST['adm'])
         adf=q.admno.split('/')[0]+'front.pdf'
         adb=q.admno.split('/')[0]+'back.pdf'
         pho=q.photo.url
         q.delete()
         os.system('rm '+pho)
         os.system('rm '+adb)
         os.system('rm '+adf)
         return render(response,'upload/home.html')
      except ObjectDoesNotExist:
         return render(request,'upload/studel.html',{"error_message":"No match found!"})
      except:
         return render(request,'upload/studel.html',{"error_message":"Deleted Succesfully"})
      context={'q':q}
      return render(request,'upload/studel.html',context)
   else:
      return render(request,'upload/studel.html')          

@login_required(login_url='/idcard/login/')
def delfac(request):
   if request.method=='POST':
      try:
         q=faculty.objects.get(name=request.POST['name'])
         pho=q.photo.url
         q.delete()
         os.system('rm '+pho)
         return render(response,'upload/home.html')
      except ObjectDoesNotExist:
         return render(request,'upload/facdel.html',{"error_message":"No match found!"})
      except:
         return render(request,'upload/facdel.html',{"error_message":"Deleted Succesfully"})
      context={'q':q}
      return render(request,'upload/facdel.html',context)
   else:
      return render(request,'upload/facdel.html')          


@login_required(login_url='/idcard/login/')
def siddesign(request):
  try:
    instance = SDesign.objects.get()
    return HttpResponseRedirect('/idcard/pdfsdesign')
  except SDesign.DoesNotExist:
    form = Sd(request.POST or None, request.FILES or None)
    if form.is_valid():
      instance = form.save(commit=False)
      instance.save()
      return HttpResponseRedirect('/idcard/pdfsdesign')
    context = {
      "form": form,
    }
    return render(request, "upload/siddesign.html", context)
    #return HttpResponseRedirect('/pdfsdesign')


@login_required(login_url='/idcard/login/')
def pdfsdesign(request):
  try:
    instance = SDesign.objects.get()
    form = Sd(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
      instance = form.save(commit=False)
      instance.save()
    return render(request, "upload/pdfsdesign.html", {"form": form})
  except SDesign.DoesNotExist:
    return HttpResponseRedirect('/idcard/siddesign')


@login_required(login_url='/idcard/login/')
def fiddesign(request):
  try:
    instance = FDesign.objects.get()
    return HttpResponseRedirect('/idcard/pdffdesign')
  except FDesign.DoesNotExist:
    form = Fd(request.POST or None, request.FILES or None)
    if form.is_valid():
      instance = form.save(commit=False)
      instance.save()
      return HttpResponseRedirect('/idcard/pdffdesign')
    context = {
      "form": form,
    }
    return render(request, "upload/fiddesign.html", context)
    #return HttpResponseRedirect('/pdfsdesign')

@login_required(login_url='/idcard/login/')
def pdffdesign(request):
  try:
    instance = FDesign.objects.get()
    form = Fd(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
      instance = form.save(commit=False)
      instance.save()
    return render(request, "upload/pdffdesign.html", {"form": form})
  except FDesign.DoesNotExist:
    return HttpResponseRedirect('/idcard/fiddesign')

@login_required(login_url='/idcard/login/')
def flab(request):
  details = FDesign.objects.get()
        #print str(details.bdesign.url)[2:]
  back = root +'/'+str(details.bdesign)[2:]
  pic = root + '/staff-sample.jpg'
  princi = root + '/'+str(details.psign)[2:]
  logocentre = root+'/'+ str(details.ilogo)[2:]
  barcode_value = "U617513CSB99"
  barcode128 = code128.Code128(barcode_value, barHeight=50*mm, barWidth=1.5*mm)
  width = 540*mm
  height = 860*mm
        #print str(details.college)
  c = canvas.Canvas('faculty.pdf')
  c.setPageSize((width, height))
  if back:
    c.drawImage(back, 0, 0, height=height, width=width)
  #c.saveState()
  if logocentre:
    c.drawImage(logocentre, 210*mm, 750*mm, height=100*mm, width=100*mm)
  c.drawImage(pic, 170*mm, height-(540*mm), height=280*mm, width=200*mm)
  c.setFont(str(details.cfont), int(details.cfontsize))
  c.drawCentredString(width/2, 730*mm, str(details.college))
  c.setFont(str(details.addline1font), int(details.addline1fontsize))
  c.drawCentredString(width/2, 710*mm, str(details.addline1))
  c.setFont(str(details.addline2to5font), int(details.addline2to5fontsize))
  c.drawCentredString(width/2, 690*mm,str(details.addline2))
  #c.drawCentredString(width/2, height-(120*mm), "")
  c.drawCentredString(width/2, 670*mm, str(details.addline3))
  c.drawCentredString(width/2, 650*mm, str(details.addline4))
  c.drawCentredString(width/2, 630*mm, str(details.addline5))
  c.setFont(str(details.detfont), int(details.detfontsize))
  c.drawString(50*mm, 250*mm, "Name ")
  c.drawString(190*mm, 250*mm, ": AMAL MAJEED")
  c.drawString(50*mm, 150*mm, "Designation ")
  c.drawString(190*mm, 150*mm, ": Assistant Professor")
  c.setFont('Times-Bold', 60)
  c.drawString(420*mm, 20*mm, "Principal")
  c.drawImage(princi, 420*mm, 45*mm, height= 50*mm, width=80*mm)
  c.showPage()

  c.setFont(str(details.detfont), int(details.detfontsize))
  c.drawString(30*mm, 760*mm, "Address ")
  c.drawString(210*mm, 760*mm, ": FLAT 2A")
  c.drawString(210*mm, 720*mm, "  SLYLINE BUILDERS")
  c.drawString(210*mm, 680*mm, "  APJ ROAD")
  c.drawString(210*mm, 640*mm, "  EDAPPALLY TOLL,")
  c.drawString(210*mm, 600*mm, "  EDAPPALLY P.O.")
  c.drawString(210*mm, 560*mm, "  682024")
  c.drawString(30*mm, 360*mm, "Contact No. ")
  c.drawString(210*mm, 360*mm, ": 0484-2577539")
  c.drawString(210*mm, 330*mm, "  8891696434")
  c.drawString(30*mm, 280*mm, "Blood Group ")
  c.drawString(210*mm, 280*mm, ": B+")
  c.drawString(30*mm, 220*mm, "Date Of Birth ")
  c.drawString(210*mm, 220*mm, ": 18/04/1995")
  barcode128.drawOn(c, 130*mm, 60*mm)
  c.drawCentredString(width/2, 30*mm, "MECF0000")
  c.save()

  with open('faculty.pdf', 'rb') as pdf:
    response = HttpResponse(pdf.read(),content_type='application/pdf')
    response['Content-Disposition'] = 'filename=some_file.pdf'
    return response
  pdf.closed

@login_required(login_url='/idcard/login/')
def genpdf1(request):
  details = FDesign.objects.get()
  q=faculty.objects.all()
  if q.__len__()==0:
  	return render(request,'upload/home.html')
  #print str(details.bdesign.url)[2:]
  back = root +'/'+str(details.bdesign)[2:]
  princi = root + '/'+str(details.psign)[2:]
  logocentre = root+'/'+ str(details.ilogo)[2:]
  barcode_value = "MECF000"
  width = 540*mm
  height = 860*mm
        #print str(details.college)
  c = canvas.Canvas('front1.pdf')
  for i in q:
    pic =i.photo.url
    c.setPageSize((width, height))
    if back:
      c.drawImage(back, 0, 0, height=height, width=width)
    #c.saveState()
    if logocentre:
      c.drawImage(logocentre, 210*mm, 750*mm, height=100*mm, width=100*mm)
    c.drawImage(pic, 170*mm, height-(540*mm), height=280*mm, width=200*mm)
    c.setFont(str(details.cfont), int(details.cfontsize))
    c.drawCentredString(width/2, 730*mm, str(details.college))
    c.setFont(str(details.addline1font), int(details.addline1fontsize))
    c.drawCentredString(width/2, 710*mm, str(details.addline1))
    c.setFont(str(details.addline2to5font), int(details.addline2to5fontsize))
    c.drawCentredString(width/2, 690*mm,str(details.addline2))
    #c.drawCentredString(width/2, height-(120*mm), "")
    c.drawCentredString(width/2, 670*mm, str(details.addline3))
    c.drawCentredString(width/2, 650*mm, str(details.addline4))
    c.drawCentredString(width/2, 630*mm, str(details.addline5))
    c.setFont(str(details.detfont), int(details.detfontsize))
    c.drawString(50*mm, 250*mm, "Name ")
    c.drawString(190*mm, 250*mm,i.name)
    c.drawString(50*mm, 150*mm, "Designation ")
    c.drawString(190*mm, 150*mm,i.designation)
    c.setFont('Times-Bold', 60)
    c.drawString(420*mm, 20*mm, "Principal")
    c.drawImage(princi, 420*mm, 45*mm, height= 50*mm, width=80*mm)
    c.showPage()
  c.save()
  c = canvas.Canvas('back1.pdf')
  for i in q:
    c.setPageSize((width, height))
    c.setFont(str(details.detfont), int(details.detfontsize))
    c.drawString(30*mm, 760*mm, "Address ")
    #le=i.address.__len__()
    n=0
        #x=2
    ht=760
    y=re.split(',',i.address)
    for x in y:
	  c.drawString(210*mm, ht*mm,x)
	  ht=ht-40
    c.drawString(30*mm, 360*mm, "Contact No. ")
    c.drawString(210*mm, 360*mm,i.contact)
    c.drawString(30*mm, 280*mm, "Blood Group ")
    c.drawString(210*mm, 280*mm, i.bloodgroup)
    c.drawString(30*mm, 220*mm, "Date Of Birth ")
    c.drawString(210*mm, 220*mm,str(i.dateofbirth.day)+'/'+str(i.dateofbirth.month)+'/'+str(i.dateofbirth.year))
    barcode128 = code128.Code128(barcode_value+str(i.pk), barHeight=50*mm, barWidth=1.5*mm)
    barcode128.drawOn(c, 130*mm, 60*mm)
    c.drawCentredString(width/2, 30*mm, "MECF000"+str(i.pk))
    c.showPage()
  c.save()
  arch=zipfile.ZipFile("id1.zip","w")
  arch.write('front1.pdf')
  arch.write('back1.pdf')
  arch.close()
  response = HttpResponse(open(root+'/id1.zip', 'rb').read(), content_type='application/zip')
  response['Content-Disposition'] = 'attachment; filename=simple1.zip'
  return response
  return render(request,'upload/home.html')

@login_required(login_url='/idcard/login/')
def liststud(request):
   q=stud.objects.all()
   if q.__len__()==0:
   	return render(request,'upload/home.html')   
   return render(request,'upload/liststud.html',{'students':stud.objects.all()})

@login_required(login_url='/idcard/login/')
def listfac(request):
   q=faculty.objects.all()
   if q.__len__()==0:
   	return render(request,'upload/home.html')   
   return render(request,'upload/listfac.html',{'faculty':faculty.objects.all()})

@login_required(login_url='/idcard/login/')
def singlestud(request):
  if request.method=="POST":
    details=SDesign.objects.get()
    if details is None:
      return HttpResponseRedirect('/idcard/pdfsdesign')
    else:
      form=SingleStud(request.POST,request.FILES)
      if form.is_valid():
        instance=form.save(commit=False)
        instance.save()
      else:
        form=SingleStud()
        context={"form":form,"error_message":"Either "+request.POST['admno']+" exists or Form syntax is invalid"}
        return render(request,'upload/singlestud.html',context)
      i=stud.objects.get(admno=request.POST['admno'])
      back = root +'/'+str(details.bdesign)[2:]
      princi = root + '/'+str(details.psign)[2:]
      logoright = root+'/'+ str(details.ilogo)[2:]
      logoleft = root +'/'+ str(details.clogo)[2:]
      width = 540*mm
      height = 860*mm
      c = canvas.Canvas(str(i.admno).split('/')[0]+'front.pdf')
      pic =i.photo.url
      c.setPageSize((width, height))
      if back:
        c.drawImage(back, 0, 0, height=height, width=width)
    #c.saveState()
      if logoleft:
        c.drawImage(logoleft, 20*mm, 740*mm, height=80*mm, width=80*mm)
      if logoright:
        c.drawImage(logoright, 450*mm, 740*mm, height=80*mm, width=80*mm)
      c.setFont(str(details.cfont), int(details.cfontsize))
      c.drawCentredString(width/2, height-(60*mm),str(details.college))
      c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
      c.drawCentredString(width/2, height-(80*mm),str(details.addline1))
      c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
      c.drawCentredString(width/2, height-(100*mm), str(details.addline2))
      #c.drawCentredString(width/2, height-(120*mm), "")  Kerala, India, PIN: 682 021 
      c.drawCentredString(width/2, height-(120*mm),str(details.addline3))
      c.drawCentredString(width/2, height-(140*mm),str(details.addline4))
      c.setFont(str(details.addline1to5font), int(details.addline1to5fontsize))
      c.drawCentredString(width/2, height-(160*mm), str(details.addline5))
      c.drawImage(pic, 170*mm, height-(375*mm), height=200*mm, width=200*mm)
      c.setFont(str(details.detfont), int(details.detfontsize))
      c.drawString(30*mm, 430*mm, "Name ")
      c.drawString(165*mm, 430*mm,i.name)
      c.setFont(str(details.detfont), int(details.detfontsize))
      c.drawString(30*mm, 340*mm, "Course :")
      c.drawString(165*mm, 340*mm,i.course)
      c.drawString(30*mm, 280*mm, "Branch :")
      c.drawString(165*mm, 280*mm, i.branch)
      c.drawString(30*mm, 180*mm, "ADMN No :")
      c.drawString(165*mm, 180*mm, i.admno)
      c.drawString(30*mm, 120*mm, "Valid Till:")
      c.drawString(165*mm, 120*mm,str(i.validtill.day)+'/'+str(i.validtill.month)+'/'+str(i.validtill.year))
      c.drawString(30*mm, 60*mm, "Date Of Birth:")
      c.drawString(165*mm, 60*mm,str(i.dateofbirth.day)+'/'+str(i.dateofbirth.month)+'/'+str(i.dateofbirth.year))
      c.setFont('Times-Bold', 60)
      c.drawString(420*mm, 20*mm, "Principal")
      if princi:
        c.drawImage(princi, 420*mm, 45*mm, height= 50*mm, width=80*mm)
      c.showPage()
      c.save()
      c = canvas.Canvas(str(i.admno).split('/')[0]+'back.pdf')
      barcode_value = ""
      if(i.course[0]=="B"):
        barcode_value+="U"
      else:
        barcode_value+="P"
      barcode_value+=i.admno.split('/')[0]+i.admno.split('/')[1]
      barcode_value+=str(i.clss)
      barcode_value+=str(i.rollno)
      barcode128 = code128.Code128(barcode_value, barHeight=50*mm, barWidth=1.5*mm)
      c.setPageSize((width, height))
      c.setFont(str(details.detfont), int(details.detfontsize))
      barcode128.drawOn(c, 130*mm, 750*mm)
      c.drawString(190*mm, 720*mm, barcode_value)
      c.drawString(30*mm, 630*mm, "Blood Group ")
      c.drawString(210*mm, 630*mm,i.bloodgroup)
      c.drawString(30*mm, 550*mm, "Address ")
      #le=i.address.__len__()
      n=0
          #x=2
      ht=550
      y=re.split(',',i.address)
      for x in y:
        c.drawString(210*mm, ht*mm,x)
        ht=ht-40
      #c.drawString(210*mm, 550*mm, ": FLAT 2A")
      #c.drawString(210*mm, 500*mm, "  SLYLINE BUILDERS")
      #c.drawString(210*mm, 450*mm, "  APJ ROAD")
      #c.drawString(210*mm, 400*mm, "  EDAPPALLY TOLL,")
      #c.drawString(210*mm, 350*mm, "  EDAPPALLY P.O.")
      #c.drawString(210*mm, 300*mm, "  682024")
      c.drawString(30*mm, 170*mm, "Contact No. ")
      c.drawString(210*mm, 170*mm,i.contact1)
      c.drawString(210*mm, 140*mm,i.contact2)
      c.drawString(30*mm, 60*mm, "Signature     :")
      c.rect(160*mm,30*mm,320*mm,70*mm)
      c.showPage()
      c.save()
           ###### TO DISPLAY PDF VIA BROWSER  ###
           #with open('amal.pdf', 'rb') as pdf:
           #   response = HttpResponse(pdf.read(),content_type='application/pdf')
           #   response['Content-Disposition'] = 'filename=some_file.pdf'
           #   return response
           #pdf.closed
      arch=zipfile.ZipFile("i.zip","w")
      arch.write(str(i.admno).split('/')[0]+'front.pdf')
      arch.write(str(i.admno).split('/')[0]+'back.pdf')
      arch.close()
      adf=i.admno.split('/')[0]+'front.pdf'
      adb=i.admno.split('/')[0]+'back.pdf'
      pho=i.photo.url
      i.delete()
      os.system('rm '+pho)
      os.system('rm '+adb)
      os.system('rm '+adf)
      response = HttpResponse(open(root+'/i.zip', 'rb').read(), content_type='application/zip')
      response['Content-Disposition'] = 'attachment; filename=single.zip'
      return response
      return render(request,'upload/home.html') 
  else:
    form=SingleStud()
    return render(request,'upload/singlestud.html',{'form':form})


  