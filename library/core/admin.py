from django.contrib import admin
from .models import User,Notification,OneTimePassword,Book,BorrowingHistory,Reservation,Fine,Feedback,Admin,Student,Resident




admin.site.register(User)
admin.site.register(Notification)
admin.site.register(OneTimePassword)
admin.site.register(Book)
admin.site.register(BorrowingHistory)
admin.site.register(Reservation)
admin.site.register(Student)
admin.site.register(Resident)
admin.site.register(Feedback)
admin.site.register(Fine)
admin.site.register(Admin)
















