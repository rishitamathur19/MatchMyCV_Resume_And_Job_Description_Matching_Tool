from django.shortcuts import render
import fitz  # For PDF
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def clean_and_tokenize(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    return [word for word in words if word.isalpha() and word not in stop_words]

def home(request):
    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        job_description = request.POST.get('job_description')

        resume_text = ''
        if resume_file and resume_file.name.endswith('.pdf'):
            with fitz.open(stream=resume_file.read(), filetype="pdf") as doc:
                for page in doc:
                    resume_text += page.get_text()

        # NLP Processing
        resume_tokens = clean_and_tokenize(resume_text)
        jd_tokens = clean_and_tokenize(job_description)

        jd_keywords = set(jd_tokens)
        resume_words = set(resume_tokens)

        matched_keywords = jd_keywords.intersection(resume_words)
        missing_keywords = jd_keywords.difference(resume_words)

        match_percentage = round((len(matched_keywords) / len(jd_keywords)) * 100, 2) if jd_keywords else 0

        context = {
            'resume_text': resume_text,
            'job_description': job_description,
            'match_percentage': match_percentage,
            'matched_keywords': sorted(matched_keywords),
            'missing_keywords': sorted(missing_keywords),
        }

        return render(request, 'scanner/result.html', context)

    return render(request, 'scanner/home.html')

def download_pdf(request):
    if request.method == 'POST':
        resume_text = request.POST.get('resume_text', '')
        job_description = request.POST.get('job_description', '')
        match_percentage = float(request.POST.get('match_percentage', 0))
        matched_keywords = request.POST.getlist('matched_keywords')
        missing_keywords = request.POST.getlist('missing_keywords')

        context = {
            'resume_text': resume_text,
            'job_description': job_description,
            'match_percentage': match_percentage,
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords
        }

        template = get_template('scanner/report_template.html')
        html = template.render(context)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="match_report.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('PDF generation failed')
        return response

    #If not a POST request, redirect or show error
    return HttpResponse("Invalid request method", status=405)