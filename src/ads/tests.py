from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils.translation import override

from ads.forms import ExchangeProposalForm
from ads.models import Ads, Category, ExchangeProposal
from core.enums import ConditionEnums, StatusEnums


class AdsCreateViewTests(TestCase):

    def setUp(self):
        """Создаем пользователя перед каждым тестом"""
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")

        self.data = {
            'title': 'Test Ad',
            'description': 'This is a test ad',
            'category': 1,
            'condition': 'new',
            'image_url': 'http://example.com/image.jpg',
        }

    def test_ads_create_view_authenticated(self):
        """Тест для авторизованного пользователя"""
        # Логинимся как тестовый пользователь
        self.client.login(username="testuser", password="testpassword")

        # Делаем запрос на создание объявления
        response = self.client.post(reverse('ads:ads-create'), self.data)

        # Проверяем, что редирект на страницу списка объявлений
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ads:ads-list'))

        # Проверяем, что объект был создан в базе данных
        self.assertEqual(Ads.objects.count(), 1)
        ad = Ads.objects.first()
        self.assertEqual(ad.title, 'Test Ad')
        self.assertEqual(ad.owner, self.user)

    def test_ads_create_view_unauthenticated(self):
        """Тест для неавторизованного пользователя"""
        # Делаем запрос на создание объявления без авторизации
        response = self.client.post(reverse('ads:ads-create'), self.data)

        # Проверяем, что пользователь перенаправляется на страницу входа
        self.assertEqual(response.status_code, 302)

        # Исправленный путь для редиректа
        self.assertRedirects(response, '/users/login/?next=/ads/create/')


class AdsListViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Электроника')

        self.ad1 = Ads.objects.create(
            title='iPhone 12',
            description='Отличное состояние',
            category=self.category,
            condition=ConditionEnums.USED,
            owner=self.user
        )
        self.ad2 = Ads.objects.create(
            title='MacBook Pro',
            description='Как новый',
            category=self.category,
            condition=ConditionEnums.NEW,
            owner=self.user
        )

    def test_ads_list_view_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('ads:ads-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone 12')
        self.assertContains(response, 'MacBook Pro')
        self.assertEqual(len(response.context['object_list']), 2)

    def test_ads_list_view_filter_by_query(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('ads:ads-list'), {'q': 'iPhone'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'iPhone 12')
        self.assertNotContains(response, 'MacBook Pro')

    def test_ads_list_view_filter_by_category(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('ads:ads-list'), {'category': self.category.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 2)

    def test_ads_list_view_filter_by_condition(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('ads:ads-list'), {'condition': ConditionEnums.NEW})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MacBook Pro')
        self.assertNotContains(response, 'iPhone 12')

    def test_ads_list_view_unauthenticated_redirect(self):
        response = self.client.get(reverse('ads:ads-list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)


class AdsUpdateViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Пользователи
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass')

        # Категория
        self.category = Category.objects.create(name='Техника')

        # Объявление
        self.ad = Ads.objects.create(
            title='Старый ноутбук',
            description='Ещё работает',
            category=self.category,
            condition=ConditionEnums.USED,
            owner=self.owner
        )

        self.url = reverse('ads:ads-update', args=[self.ad.pk])

    def test_update_view_owner_access(self):
        self.client.login(username='owner', password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Старый ноутбук')

    def test_update_view_superuser_access(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Старый ноутбук')

    def test_update_view_other_user_forbidden(self):
        self.client.login(username='other', password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # or redirect/404 based on your mixin

    def test_update_post_owner(self):
        self.client.login(username='owner', password='pass')
        response = self.client.post(self.url, {
            'title': 'Обновлённый ноутбук',
            'description': 'Теперь лучше',
            'category': self.category.pk,
            'condition': ConditionEnums.NEW,
        })
        self.assertRedirects(response, reverse('ads:ads-list'))

        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Обновлённый ноутбук')
        self.assertEqual(self.ad.condition, ConditionEnums.NEW)

    def test_update_unauthenticated_redirect(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)


class AdsDeleteViewTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.owner = User.objects.create_user(username='owner', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')
        self.superuser = User.objects.create_superuser(username='admin', password='adminpass')

        self.category = Category.objects.create(name='Электроника')

        self.ad = Ads.objects.create(
            title='Смартфон',
            description='Почти новый',
            category=self.category,
            condition=ConditionEnums.USED,
            owner=self.owner
        )

        self.url = reverse('ads:ads-delete', args=[self.ad.pk])
        self.success_url = reverse('ads:ads-list')

    def test_delete_view_owner_access(self):
        self.client.login(username='owner', password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_delete_owner_post(self):
        self.client.login(username='owner', password='pass')
        response = self.client.post(self.url)
        self.assertRedirects(response, self.success_url)
        self.assertFalse(Ads.objects.filter(pk=self.ad.pk).exists())

    def test_delete_superuser_access(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_delete_superuser_post(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(self.url)
        self.assertRedirects(response, self.success_url)
        self.assertFalse(Ads.objects.filter(pk=self.ad.pk).exists())

    def test_delete_other_user_forbidden(self):
        self.client.login(username='other', password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # или 404, если mixin скрывает объект

    def test_delete_unauthenticated_redirect(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)


class ExchangeProposalCreateViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Электроника")
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        self.ad = Ads.objects.create(
            title='Ноутбук',
            description='MacBook Pro',
            owner=self.other_user,
            category=self.category
        )
        self.url = reverse('ads:offer-create', kwargs={'pk': self.ad.pk})

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/users/login/?next={self.url}')

    def test_view_renders_for_authenticated_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/ads_form.html')
        self.assertIsInstance(response.context['form'], ExchangeProposalForm)

    def test_successful_proposal_creation(self):
        self.client.login(username='testuser', password='password')

        sender_ad = Ads.objects.create(
            title='Телефон',
            description='iPhone',
            owner=self.user,
            category=self.category
        )

        data = {
            'ad_sender': sender_ad.pk,
            'comment': 'Готов обменять на ноутбук'
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('ads:ads-list'))
        self.assertEqual(ExchangeProposal.objects.count(), 1)
        proposal = ExchangeProposal.objects.first()
        self.assertEqual(proposal.ad_receiver, self.ad)
        self.assertEqual(proposal.comment, 'Готов обменять на ноутбук')

    def test_invalid_ad_receiver_id(self):
        self.client.login(username='testuser', password='password')
        bad_url = reverse('ads:offer-create', kwargs={'pk': 9999})
        response = self.client.post(bad_url, {})
        self.assertEqual(response.status_code, 404)

    def test_invalid_form_does_not_create_proposal(self):
        with override('ru'):
            self.client.login(username='testuser', password='password')
            response = self.client.post(self.url, {'comment': 'Обмен!'})
            response.render()  # форсируем рендеринг шаблона
            form = response.context['form']
            self.assertFormError(form, 'ad_sender', 'Обязательное поле.')
            self.assertEqual(ExchangeProposal.objects.count(), 0)


class ExchangeProposalListViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Электроника")
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')

        self.ad1 = Ads.objects.create(
            title='Ноутбук',
            description='MacBook Pro',
            owner=self.user,
            category=self.category
        )
        self.ad2 = Ads.objects.create(
            title='Телефон',
            description='iPhone',
            owner=self.other_user,
            category=self.category
        )

        self.proposal1 = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            status=StatusEnums.WAITING
        )
        self.proposal2 = ExchangeProposal.objects.create(
            ad_sender=self.ad2,
            ad_receiver=self.ad1,
            status=StatusEnums.ACCEPTED
        )

        self.url = reverse('ads:offer-list')

    def test_view_requires_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/users/login/?next={self.url}')

    def test_view_renders_for_authenticated_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/exchangeproposal_list.html')
        self.assertIn('statuses', response.context)
        self.assertIn('ad_receivers', response.context)
        self.assertIn('ad_senders', response.context)

    def test_filter_by_status(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url, {'status': StatusEnums.WAITING})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['object_list'],
            [self.proposal1],
            transform=lambda x: x
        )

    def test_filter_by_ad_sender(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url, {'ad_sender': self.ad1.id})
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            list(map(repr, response.context['object_list'])),
            [repr(self.proposal1)]
        )

    def test_filter_by_ad_receiver(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url, {'ad_receiver': self.ad2.id})
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            list(map(repr, response.context['object_list'])),
            [repr(self.proposal1)]
        )

    def test_filter_by_multiple_params(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url, {'status': StatusEnums.WAITING, 'ad_sender': self.ad1.id})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['object_list'],
            [self.proposal1],
            transform=lambda x: x
        )

    def test_filter_no_results(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url, {'status': StatusEnums.REJECTED})
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context['object_list'], [])

    def test_ad_receivers_in_context(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.proposal1, response.context['ad_receivers'])

    def test_ad_senders_in_context(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.proposal2, response.context['ad_senders'])


class ExchangeProposalViewsTest(TestCase):

    def setUp(self):
        # Создание пользователей
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='testotheruser', password='password')
        self.superuser = User.objects.create_superuser(username='admin', password='password')

        # Создание категории
        self.category = Category.objects.create(name="Общая")

        # Создание объявлений с категорией
        self.ad_sender = Ads.objects.create(
            owner=self.user,
            title="Ad Sender",
            category=self.category
        )
        self.ad_receiverother = Ads.objects.create(
            owner=self.other_user,
            title="Ad other_user",
            category=self.category
        )

        self.ad_receiver = Ads.objects.create(
            owner=self.superuser,
            title="Ad Receiver",
            category=self.category
        )

        # Создание предложения
        self.proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad_sender,
            ad_receiver=self.ad_receiver,
            status=StatusEnums.WAITING
        )

        # URL'ы для тестов
        self.delete_url = reverse('ads:offer-delete', kwargs={'pk': self.proposal.pk})
        self.accept_url = reverse('ads:offer-accept', kwargs={'pk': self.proposal.pk})
        self.reject_url = reverse('ads:offer-reject', kwargs={'pk': self.proposal.pk})

    def test_delete_proposal_as_superuser(self):
        # Тестируем, что суперпользователь может удалить предложение
        self.client.login(username='admin', password='password')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse('ads:offer-list'))  # success_url указан для списка предложений
        self.assertFalse(ExchangeProposal.objects.filter(pk=self.proposal.pk).exists())

    def test_delete_proposal_as_normal_user(self):
        # Логинимся как обычный пользователь
        self.client.login(username='testuserother', password='password')
        # Создаем предложение с этим объявлением
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad_sender,
            ad_receiver=self.ad_receiverother,
        )
        # Формируем URL для удаления предложения
        url = reverse('ads:offer-delete', kwargs={'pk': proposal.pk})
        # Отправляем DELETE-запрос на удаление
        response = self.client.delete(url)
        # Проверяем, что доступ запрещен
        self.assertEqual(response.status_code, 403)

    def test_accept_proposal(self):
        # Тестируем, что можно принять предложение
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.accept_url)
        self.assertRedirects(response, reverse('ads:offer-list'))
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, StatusEnums.ACCEPTED)

    def test_reject_proposal(self):
        # Тестируем, что можно отклонить предложение
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.reject_url)
        self.assertRedirects(response, reverse('ads:offer-list'))
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, StatusEnums.REJECTED)

    def test_accept_proposal_not_logged_in(self):
        # Тестируем, что если пользователь не залогинен, то он будет перенаправлен на страницу входа
        response = self.client.get(self.accept_url, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/?next=', response['Location'])

    def test_reject_proposal_not_logged_in(self):
        # Тестируем, что если пользователь не залогинен, то он будет перенаправлен на страницу входа
        response = self.client.get(self.accept_url, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/users/login/?next=', response['Location'])
