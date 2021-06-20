from django.db import models

class Call(models.Model):
    direction_choices = [
        ('C2S', 'Client to Server'),
        ('S2C', 'Server to Client'),
    ]

    message_type_id = models.IntegerField()
    message_id = models.CharField(max_length=36)
    action = models.CharField(max_length=70)
    payload = models.TextField()

    charger_id = models.CharField(max_length=100, default='')
    sent_at = models.DateTimeField(auto_now_add=True, blank=True)
    direction = models.CharField(max_length=3, choices=direction_choices, blank=True)

    call_result_obj = models.OneToOneField('CallResult', on_delete=models.CASCADE, null=True)

class CallResult(models.Model):
    direction_choices = [
        ('C2S', 'Client to Server'),
        ('S2C', 'Server to Client'),
    ]

    message_type_id = models.IntegerField()
    message_id = models.CharField(max_length=36)
    payload = models.TextField()

    charger_id = models.CharField(max_length=100, default='')
    sent_at = models.DateTimeField(auto_now_add=True, blank=True)
    direction = models.CharField(max_length=3, choices=direction_choices, blank=True)

    call_obj = models.OneToOneField('Call', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'({self.id}) {"Accepted" if "Accepted" in self.payload or len(self.payload) == 2 else "Rejected"}'