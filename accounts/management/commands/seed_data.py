"""
Management command to populate database with sample dummy data.
Creates users, diseases, recommendations, detections, and messages.
Usage: python manage.py seed_data
"""

import sys
import io
from django.core.management.base import BaseCommand
from accounts.models import User
from detection.models import Disease, Recommendation, Detection
from messaging.models import ChatMessage


class Command(BaseCommand):
    help = 'Seeds database with sample data for AgriSmart AI'

    def handle(self, *args, **options):
        # Fix Windows console encoding
        if sys.platform == 'win32':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

        self.stdout.write('[*] Seeding database...\n')

        # --- Create Users ---
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@agrismart.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': User.Role.ADMIN,
                'district': 'Dhaka',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('  [OK] Admin: admin / admin123'))

        officer, created = User.objects.get_or_create(
            username='officer1',
            defaults={
                'email': 'officer@agrismart.com',
                'first_name': 'Karim',
                'last_name': 'Uddin',
                'role': User.Role.OFFICER,
                'district': 'Rajshahi',
                'phone': '01712345678',
            }
        )
        if created:
            officer.set_password('officer123')
            officer.save()
            self.stdout.write(self.style.SUCCESS('  [OK] Officer: officer1 / officer123'))

        farmer, created = User.objects.get_or_create(
            username='farmer1',
            defaults={
                'email': 'farmer@agrismart.com',
                'first_name': 'Rahim',
                'last_name': 'Mia',
                'role': User.Role.FARMER,
                'district': 'Bogura',
                'phone': '01812345678',
            }
        )
        if created:
            farmer.set_password('farmer123')
            farmer.save()
            self.stdout.write(self.style.SUCCESS('  [OK] Farmer: farmer1 / farmer123'))

        farmer2, created = User.objects.get_or_create(
            username='farmer2',
            defaults={
                'email': 'farmer2@agrismart.com',
                'first_name': 'Jamal',
                'last_name': 'Hossain',
                'role': User.Role.FARMER,
                'district': 'Dinajpur',
                'phone': '01912345678',
            }
        )
        if created:
            farmer2.set_password('farmer123')
            farmer2.save()
            self.stdout.write(self.style.SUCCESS('  [OK] Farmer: farmer2 / farmer123'))

        # --- Create Diseases ---
        diseases_data = [
            {
                'name_bn': 'ধানের ব্লাস্ট রোগ',
                'name_en': 'Rice Blast',
                'description_bn': 'ধানের পাতায় ডিম্বাকৃতির দাগ দেখা যায়। দাগগুলো ধূসর কেন্দ্রবিশিষ্ট এবং বাদামি রঙের প্রান্ত থাকে।',
                'crop_type': 'ধান',
                'severity': 'high',
                'treatment': 'ট্রাইসাইক্লাজোল (Beam 75WP) প্রতি লিটার পানিতে ০.৫ গ্রাম মিশিয়ে স্প্রে করুন।',
                'pesticide': 'ট্রাইসাইক্লাজোল (Beam 75WP), কার্বেন্ডাজিম',
                'prevention': 'রোগ প্রতিরোধী জাত ব্যবহার করুন। অতিরিক্ত ইউরিয়া সার ব্যবহার এড়িয়ে চলুন।',
            },
            {
                'name_bn': 'টমেটোর আগাম ধসা রোগ',
                'name_en': 'Tomato Early Blight',
                'description_bn': 'পাতায় গোলাকার বাদামি-কালো দাগ দেখা যায়। দাগে রিং আকৃতির স্তর থাকে।',
                'crop_type': 'টমেটো',
                'severity': 'medium',
                'treatment': 'ম্যানকোজেব (Dithane M-45) প্রতি লিটার পানিতে ২ গ্রাম মিশিয়ে স্প্রে করুন।',
                'pesticide': 'ম্যানকোজেব, ক্লোরোথালোনিল',
                'prevention': 'সুষম সার ব্যবহার করুন। আক্রান্ত পাতা সংগ্রহ করে পুড়িয়ে ফেলুন।',
            },
            {
                'name_bn': 'ভুট্টার পাতা ঝলসানো রোগ',
                'name_en': 'Corn Leaf Blight',
                'description_bn': 'পাতায় লম্বাটে ধূসর-সবুজ দাগ দেখা যায় যা পরে বাদামি হয়ে যায়।',
                'crop_type': 'ভুট্টা',
                'severity': 'medium',
                'treatment': 'প্রোপিকোনাজোল (Tilt 250EC) প্রতি লিটার পানিতে ০.৫ মিলি মিশিয়ে স্প্রে করুন।',
                'pesticide': 'প্রোপিকোনাজোল, অ্যাজোক্সিস্ট্রবিন',
                'prevention': 'ফসল পর্যায়ক্রম অনুসরণ করুন। রোগমুক্ত বীজ ব্যবহার করুন।',
            },
            {
                'name_bn': 'আলুর নাবি ধসা রোগ',
                'name_en': 'Potato Late Blight',
                'description_bn': 'পাতার প্রান্তে বা কিনারায় জলসিক্ত দাগ দেখা যায়। আর্দ্র আবহাওয়ায় পাতার নিচে সাদা ছত্রাক দেখা যায়।',
                'crop_type': 'আলু',
                'severity': 'critical',
                'treatment': 'মেটালাক্সিল + ম্যানকোজেব (Ridomil Gold) প্রতি লিটার পানিতে ২ গ্রাম মিশিয়ে স্প্রে করুন।',
                'pesticide': 'মেটালাক্সিল + ম্যানকোজেব (Ridomil Gold MZ 68WG)',
                'prevention': 'প্রতিরোধী জাত চাষ করুন। জমিতে পানি জমতে দেবেন না।',
            },
            {
                'name_bn': 'গমের মরিচা রোগ',
                'name_en': 'Wheat Rust',
                'description_bn': 'পাতায় ও কাণ্ডে মরিচার মতো বাদামি-লাল গুঁড়ি দেখা যায়।',
                'crop_type': 'গম',
                'severity': 'high',
                'treatment': 'টেবুকোনাজোল (Folicur 250EC) প্রতি লিটার পানিতে ১ মিলি মিশিয়ে স্প্রে করুন।',
                'pesticide': 'টেবুকোনাজোল, প্রোপিকোনাজোল',
                'prevention': 'রোগ প্রতিরোধী জাত ব্যবহার করুন। সঠিক সময়ে বপন করুন।',
            },
            {
                'name_bn': 'সুস্থ পাতা',
                'name_en': 'Healthy Leaf',
                'description_bn': 'পাতায় কোনো রোগের লক্ষণ পাওয়া যায়নি। পাতা সম্পূর্ণ সুস্থ।',
                'crop_type': 'সাধারণ',
                'severity': 'low',
                'treatment': 'কোনো চিকিৎসার প্রয়োজন নেই। নিয়মিত পরিচর্যা চালিয়ে যান।',
                'pesticide': 'প্রযোজ্য নয়',
                'prevention': 'সুষম সার ব্যবহার, সঠিক সেচ এবং নিয়মিত পর্যবেক্ষণ করুন।',
            },
        ]

        for d_data in diseases_data:
            disease, created = Disease.objects.get_or_create(
                name_en=d_data['name_en'],
                defaults={
                    'name_bn': d_data['name_bn'],
                    'description_bn': d_data['description_bn'],
                    'crop_type': d_data['crop_type'],
                    'severity': d_data['severity'],
                }
            )
            if created:
                Recommendation.objects.create(
                    disease=disease,
                    treatment_bn=d_data['treatment'],
                    pesticide_bn=d_data['pesticide'],
                    prevention_bn=d_data['prevention'],
                )
                self.stdout.write(self.style.SUCCESS(f'  [OK] Disease: {disease.name_en}'))

        # --- Create Sample Chat Messages ---
        # if not ChatMessage.objects.exists():
        #     ChatMessage.objects.create(
        #         sender=farmer,
        #         receiver=officer,
        #         message='স্যার, আমার ধানের পাতায় দাগ দেখা যাচ্ছে। কী করব?',
        #     )
        #     ChatMessage.objects.create(
        #         sender=officer,
        #         receiver=farmer,
        #         message='পাতার ছবি আপলোড করুন। আমি দেখে পরামর্শ দেব।',
        #     )
        #     ChatMessage.objects.create(
        #         sender=farmer,
        #         receiver=officer,
        #         message='ধন্যবাদ স্যার। ছবি আপলোড করেছি।',
        #     )
        #     self.stdout.write(self.style.SUCCESS('  [OK] Sample chat messages created'))

        self.stdout.write(self.style.SUCCESS('\n[DONE] Database seeded successfully!'))
        self.stdout.write('\nLogin Credentials:')
        self.stdout.write('  Admin:   admin / admin123')
        self.stdout.write('  Officer: officer1 / officer123')
        self.stdout.write('  Farmer:  farmer1 / farmer123')
        self.stdout.write('  Farmer:  farmer2 / farmer123')
