from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
# Register your models here.
from import_export import resources

from .models import User,Question,TestAttempt
admin.site.register(User)
class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'option1', 'option2', 'option3', 'option4', 'correct_answer')
        export_order = ('id', 'question_text', 'option1', 'option2', 'option3', 'option4', 'correct_answer')

@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = ('question_text', 'correct_answer')
    search_fields = ('question_text',)
    list_per_page = 20
admin.site.register(TestAttempt)
