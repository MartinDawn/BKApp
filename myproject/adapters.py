from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied

class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email', '')
        print(sociallogin.account.extra_data)
        if not email.endswith('.edu.vn'):
            raise PermissionDenied("Bạn cần dùng tài khoản nhà trường để đăng nhập")

    def populate_user(self, request, sociallogin, data):
        """
        Hàm này được allauth gọi sau khi đăng nhập thành công
        để "nhồi" data từ Google vào model User.
        """
        # Lấy đối tượng user (có thể là user mới hoặc cũ)
        user = super().populate_user(request, sociallogin, data)

        # Lấy data từ Google (data này cũng nằm trong sociallogin.account.extra_data)
        full_name = data.get('name')
        picture = data.get('picture')
        email = data.get('email')

        # --- ĐỒNG BỘ DATA ---
        
        # Chỉ cập nhật nếu User.first_name đang rỗng
        if full_name and not user.first_name:
            parts = full_name.split()
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = ' '.join(parts[1:])
        
        # Bạn cũng có thể cập nhật email (nếu logic của bạn cần)
        if email and not user.email:
             user.email = email

        # (Lưu ý: Chúng ta không lưu 'picture' vào User,
        # vì view MeView đã lấy nó từ extra_data, như vậy là tốt rồi)
        
        # Trả về user đã được cập nhật
        return user