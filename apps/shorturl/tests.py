from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ShortUrls
from .services import ShortUrlGenerater


class ShortUrlGeneraterTests(APITestCase):
    """
    1. 測試服務層 (Service Layer)
    測試核心的編碼/解碼邏輯
    """

    def test_encode_and_decode(self):
        """測試 encode 和 decode 是否能正確地互相轉換"""
        test_ids = [0, 1, 61, 62, 12345, 987654321]

        for original_id in test_ids:
            # 使用 with self.subTest(...) 可以在一個測試方法中執行多個子測試
            with self.subTest(original_id=original_id):
                short_code = ShortUrlGenerater.encode(original_id)
                decoded_id = ShortUrlGenerater.decode(short_code)
                self.assertEqual(original_id, decoded_id)

    def test_decode_invalid_character(self):
        """測試 decode 遇到無效字元時是否會拋出 ValueError"""
        # CHAR_SET 中不包含 '#' 和 '!'
        invalid_code = 'a#b!'
        with self.assertRaises(ValueError):
            ShortUrlGenerater.decode(invalid_code)


class ShortUrlsAPITests(APITestCase):
    """
    2. 測試視圖層 (View/API Layer) - CRUD API
    測試 /api/shorturls/ 的端點
    """

    def setUp(self):
        """在每個測試方法執行前，先建立一些測試資料"""
        self.url1 = ShortUrls.objects.create(original_url='https://www.google.com')
        self.url2 = ShortUrls.objects.create(original_url='https://www.djangoproject.com')

    def test_create_short_url(self):
        """測試 POST /api/shorturls/ - 建立新的短網址"""
        url = reverse('shorturls-list')  # DRF router 會自動產生 'basename-list' 的 URL name
        data = {'original_url': 'https://docs.python.org'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShortUrls.objects.count(), 3)
        self.assertEqual(response.data['original_url'], data['original_url'])

        # 驗證回傳的 short_url 是否為完整的絕對 URL
        new_id = response.data['id']
        expected_short_code = ShortUrlGenerater.encode(new_id)
        self.assertIn(expected_short_code, response.data['short_url'])
        self.assertTrue(response.data['short_url'].startswith('http://'))

    def test_list_short_urls(self):
        """測試 GET /api/shorturls/ - 獲取短網址列表"""
        url = reverse('shorturls-list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 你的 settings.py 中設定了 PAGE_SIZE=3，所以這裡應該是 2 筆
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['count'], 2)

    def test_retrieve_short_url(self):
        """測試 GET /api/shorturls/{pk}/ - 獲取單一短網址"""
        url = reverse('shorturls-detail', kwargs={'pk': self.url1.pk})
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['original_url'], self.url1.original_url)

    def test_soft_delete_short_url(self):
        """測試 DELETE /api/shorturls/{pk}/ - 軟刪除"""
        url = reverse('shorturls-detail', kwargs={'pk': self.url1.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 重新從資料庫獲取 instance 來確認 is_deleted 狀態
        self.url1.refresh_from_db()
        self.assertTrue(self.url1.is_deleted)

        # 驗證 ActiveManager 是否生效，軟刪除的資料不應該出現在列表中
        list_url = reverse('shorturls-list')
        list_response = self.client.get(list_url)
        self.assertEqual(list_response.data['count'], 1)


class RedirectViewTests(APITestCase):
    """
    3. 測試視圖層 (View/API Layer) - 重定向功能
    測試 /{short_code}/ 的端點
    """

    def setUp(self):
        self.google_url = 'https://www.google.com'
        self.short_url_instance = ShortUrls.objects.create(original_url=self.google_url)
        self.short_code = ShortUrlGenerater.encode(self.short_url_instance.id)

    def test_redirect_success(self):
        """測試有效的 short_code 是否能成功重定向並增加點擊次數"""
        url = reverse('redirect', kwargs={'short_code': self.short_code})
        response = self.client.get(url)

        # 1. 驗證 HTTP 狀態碼為 302 Found (重定向)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        # 2. 驗證重定向的目標 URL 是否正確
        self.assertEqual(response.url, self.google_url)

        # 3. 驗證點擊次數是否增加
        self.short_url_instance.refresh_from_db()
        self.assertEqual(self.short_url_instance.clicks_count, 1)

        # 再次存取，驗證點擊次數會累加
        self.client.get(url)
        self.short_url_instance.refresh_from_db()
        self.assertEqual(self.short_url_instance.clicks_count, 2)

    def test_redirect_not_found(self):
        """測試無效的 short_code 是否回傳 404 Not Found"""
        # 產生一個資料庫中不存在的 ID 的 short_code
        non_existent_code = ShortUrlGenerater.encode(99999)
        url = reverse('redirect', kwargs={'short_code': non_existent_code})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 測試一個包含無效字元的 short_code
        invalid_code_url = reverse('redirect', kwargs={'short_code': '$$$'})
        response = self.client.get(invalid_code_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_redirect_inactive_url(self):
        """測試 is_active=False 的 URL 是否回傳 404"""
        self.short_url_instance.is_active = False
        self.short_url_instance.save()

        url = reverse('redirect', kwargs={'short_code': self.short_code})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_redirect_expired_url(self):
        """測試已過期的 URL 是否回傳 404"""
        # 將 expires_at 設定為過去的時間
        self.short_url_instance.expires_at = timezone.now() - timedelta(days=1)
        self.short_url_instance.save()

        url = reverse('redirect', kwargs={'short_code': self.short_code})
        response = self.client.get(url)

        # 因為 ActiveManager 會過濾掉過期的 URL，所以應該找不到
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
