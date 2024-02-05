import os
import subprocess

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.translation import gettext_lazy as _

from .methods import get_next_state, is_mediacms_editor
from .models import Media, Subtitle


class MultipleSelect(forms.CheckboxSelectMultiple):
    input_type = "checkbox"


class MediaForm(forms.ModelForm):
    new_tags = forms.CharField(label=_("Tags"), help_text=_("a comma separated list of new tags."), required=False)

    class Meta:
        model = Media
        fields = (
            "title",
            "category",
            "new_tags",
            "add_date",
            "uploaded_poster",
            "description",
            "state",
            "enable_comments",
            "featured",
            "thumbnail_time",
            "reported_times",
            "is_reviewed",
            "allow_download",
        )
        widgets = {
            "tags": MultipleSelect(),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(MediaForm, self).__init__(*args, **kwargs)
        if self.instance.media_type != "video":
            self.fields.pop("thumbnail_time")
        if not is_mediacms_editor(user):
            self.fields.pop("featured")
            self.fields.pop("reported_times")
            self.fields.pop("is_reviewed")
        self.fields["new_tags"].initial = ", ".join([tag.title for tag in self.instance.tags.all()])

    def clean_uploaded_poster(self):
        image = self.cleaned_data.get("uploaded_poster", False)
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 5mb )")
            return image

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        state = data.get("state")
        if state != self.initial["state"]:
            self.instance.state = get_next_state(self.user, self.initial["state"], self.instance.state)

        media = super(MediaForm, self).save(*args, **kwargs)
        return media


class SubtitleForm(forms.ModelForm):
    class Meta:
        model = Subtitle
        fields = ["language", "subtitle_file"]

    def __init__(self, media_item, *args, **kwargs):
        super(SubtitleForm, self).__init__(*args, **kwargs)
        self.instance.media = media_item

    def clean_subtitle_file(self):
        subtitle_file = self.cleaned_data.get("subtitle_file")

        if not subtitle_file:
            raise forms.ValidationError('No file was submitted.')

        file_extension = os.path.splitext(subtitle_file.name)[1].lower()

        if file_extension == '.vtt':
            return subtitle_file
        elif file_extension == '.srt':
            # Convert SRT to VTT
            return self.convert_srt_to_vtt(subtitle_file)

        else:
            raise forms.ValidationError('Invalid file format. Only SRT or VTT files are allowed.')

    def convert_srt_to_vtt(self, srt_file):
        base_filename, _ = os.path.splitext(srt_file.name)
        vtt_filename = f"{base_filename}.vtt"

        with srt_file.open('rb') as srt_content:
            # Run ffmpeg command to convert SRT to VTT
            try:
                process = subprocess.run(
                    ["ffmpeg", "-i", "pipe:0", "-c:s", "webvtt", "-f", "webvtt", "pipe:1"],
                    input=srt_content.read(),
                    capture_output=True,
                    check=True,
                )
                vtt_content = process.stdout.decode('utf-8')
            except subprocess.CalledProcessError as e:
                raise forms.ValidationError(f'Error converting SRT to VTT: {e}')

        # Create a temporary VTT file
        return SimpleUploadedFile(vtt_filename, vtt_content.encode('utf-8'))

    def save(self, *args, **kwargs):
        self.instance.user = self.instance.media.user
        media = super(SubtitleForm, self).save(*args, **kwargs)
        return media


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    name = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea, required=True)

    def __init__(self, user, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = _("Your name:")
        self.fields["from_email"].label = _("Your email:")
        self.fields["message"].label = _("Please add your message here and submit:")
        self.user = user
        if user.is_authenticated:
            self.fields.pop("name")
            self.fields.pop("from_email")
