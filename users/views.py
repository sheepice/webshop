import os.path
import random
import re
import time

from django.http import FileResponse
from rest_framework import status, mixins
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from common.aliiyun_message import AliyunMessage
from users.models import User, Addr, VerifCode, Area
from webshop.settings import MEDIA_ROOT
from .permissions import UserPermission, AddrPermission
from .serializers import UserSerializer, AddrSerializer, AreaSerializer
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        password_confirmation = request.data.get('password_confirmation')

        if not all([username, password, email, password_confirmation]):
            return Response({'error': "所有参数不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if User.objects.filter(username=username).exists():
            return Response({'error': "用户名已存在"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if password != password_confirmation:
            return Response({'error': "两次密码不一致"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if not (6 <= len(password) <= 18):
            return Response({'error': "密码长度需要在6到18位之间"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if User.objects.filter(email=email).exists():
            return Response({'error': "该邮箱已被其它用户使用"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9]+(\.[a-z]{2,5}){1,2}$', email):
            return Response({'error': "邮箱格式有误！"}, status=status.HTTP_400_BAD_REQUEST)

        obj = User.objects.create_user(username=username, email=email, password=password)
        res = {"username": username, 'id': obj.id, 'email': obj.email}
        return Response(res, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        # 自定义登陆成功之后返回的结果
        result = serializer.validated_data
        result['id'] = serializer.user.id
        result['mobile'] = serializer.user.mobile
        result['email'] = serializer.user.email
        result['username'] = serializer.user.username
        result['token'] = result.pop('access')

        return Response(result, status=status.HTTP_200_OK)


class UserView(GenericViewSet, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # 设置认证用户才能访问
    permission_classes = [IsAuthenticated, UserPermission]

    def upload_avatar(self, request, *args, **kwargs):
        """上传用户头像"""
        avatar = request.data.get('avatar')
        # 校验是否有上传文件
        if not avatar:
            return Response({'error': '上传失败，文件不能为空'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 校验文件大小不能超过300kb
        if avatar.size > 1024 * 300:
            return Response({'error': '上传失败，文件大小不能超过300kb'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 保存文件
        user = self.get_object()
        # 获取序列化对象
        ser = self.get_serializer(user, data={"avatar": avatar}, partial=True)
        # 校验
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({'url': ser.data['avatar']})

    @staticmethod
    def verif_code(code, codeID, mobile):
        """验证码校验的通用逻辑"""

        # 1.校验参数
        if not code:
            return {'error': "验证码不能为空"}
        if not codeID:
            return {'error': "验证码ID不能为空"}
        if not mobile:
            return {'error': "手机号不能为空"}
        # 2.校验验证码
        if VerifCode.objects.filter(id=codeID, code=code, mobile=mobile).exists():
            # 校验验证码是否过期（过期时间3分钟）
            c_obj = VerifCode.objects.get(id=codeID, code=code, mobile=mobile)
            # 获取验证码创建的时间戳
            ct = c_obj.creat_time.timestamp()
            # 获取当前时间的时间戳
            et = time.time()
            # 删除验证码（避免出现用户在有效期内，使用同一个验证码重复请求）
            c_obj.delete()
            if ct + 180 < et:
                return {'error': "验证码已过期，请重新获取验证码"}
        else:
            return {'error': "验证码验证失败，请重新获取验证码！"}

    def bind_mobile(self, request, *args, **kwargs):
        """绑定手机号"""
        # 1.获取参数
        code = request.data.get('code')
        codeID = request.data.get('codeID')
        mobile = request.data.get('mobile')

        # 2.校验参数
        if not code:
            return Response({'error': "验证码不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not codeID:
            return Response({'error': "验证码ID不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if not mobile:
            return Response({'error': "手机号不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 3.校验验证码
        if VerifCode.objects.filter(id=codeID, code=code, mobile=mobile).exists():
            # 校验验证码是否过期（过期时间3分钟）
            c_obj = VerifCode.objects.get(id=codeID, code=code, mobile=mobile)
            # 获取验证码创建的时间戳
            ct = c_obj.creat_time.timestamp()
            # 获取当前时间的时间戳
            et = time.time()
            # 删除验证码（避免出现用户在有效期内，使用同一个验证码重复请求）
            c_obj.delete()
            if ct + 180 < et:
                return Response({'error': "验证码已过期，请重新获取验证码"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            return Response({'error': "验证码验证失败，请重新获取验证码！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        if User.objects.filter(mobile=mobile).exists():
            return Response({'error': "手机号不能重复绑定"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 绑定手机号
        user = request.user
        user.mobile = mobile
        user.save()
        return Response({'message': "绑定成功"}, status=status.HTTP_200_OK)

    def unbind_mobile(self, request, *args, **kwargs):
        """解绑手机号"""
        # 1.获取参数
        code = request.data.get('code')
        codeID = request.data.get('codeID')
        mobile = request.data.get('mobile')
        # 2.校验参数和验证码
        result = self.verif_code(code, codeID, mobile)
        if result:
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 3.解绑手机（验证用户已绑定的手机号）
        user = request.user
        if user.mobile == mobile:
            user.mobile = ''
            user.save()
            return Response({'message': "解绑成功"}, status=status.HTTP_200_OK)
        else:
            return Response({'error': "当前用户没有绑定该号码"}, status=status.HTTP_400_BAD_REQUEST)

    def update_name(self, request, *args, **kwargs):
        """修改用户昵称"""
        # 获取参数
        last_name = request.data.get('last_name')
        # 校验参数
        if not last_name:
            return Response({'error': "参数last_name不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 修改用户名
        user = self.get_object()
        user.last_name = last_name
        user.save()
        return Response({'message': "修改成功"}, status=status.HTTP_200_OK)

    def update_email(self, request, *args, **kwargs):
        """修改用户邮箱的视图"""
        # 1.获取参数
        email = request.data.get('email')
        user = self.get_object()
        # 2.校验参数
        # 参数不能为空
        if not email:
            return Response({'error': "邮箱不能为空"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 校验邮箱格式是否正确
        if not re.match('^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', email):
            return Response({'error': "邮箱格式不正确"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 邮箱地址和之前的是否一样
        if user.email == email:
            return Response({'message': "OK"}, status=status.HTTP_200_OK)
        # 邮箱有没有被其它用户绑定
        if User.objects.filter(email=email).exists():
            return Response({'error': "该邮箱已被其他用户绑定"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 3.修改邮箱
        user.email = email
        user.save()
        return Response({'message': "修改邮箱成功"}, status=status.HTTP_200_OK)

    def update_password(self, request, *args, **kwargs):
        """修改密码"""
        user = self.get_object()
        # 1.获取参数
        code = request.data.get('code')
        codeID = request.data.get('codeID')
        mobile = request.data.get('mobile')
        password = request.data.get('password')
        password_confirmation = request.data.get('password_confirmation')
        # 2.校验验证码
        result = self.verif_code(code, codeID, mobile)
        if result:
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if user.mobile != mobile:
            return Response({'error': "手机号有误！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 3.校验密码
        if not password:
            return Response({'error': "密码不能为空！"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if password != password_confirmation:
            return Response({'error': "两次密码输入不一致!"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 4.修改密码
        user.set_password(password)
        user.save()

        return Response({'message': "修改密码"})


class FileView(APIView):
    """获取文件的视图"""
    def get(self, request, name):
        path = MEDIA_ROOT / name
        if os.path.isfile(path):
            return FileResponse(open(path, 'rb'))
        return Response({'code': "没有找到该文件！"}, status=status.HTTP_404_NOT_FOUND)


class AddrView(GenericViewSet,
               mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.DestroyModelMixin,
               mixins.UpdateModelMixin):
    """地址管理视图"""
    queryset = Addr.objects.all()
    serializer_class = AddrSerializer
    # 设置认证用户才能访问
    permission_classes = [IsAuthenticated, AddrPermission]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 通过请求过来的认证用户进行过滤
        queryset = queryset.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def set_default_addr(self, request, *args, **kwargs):
        """设置默认收货地址"""
        # 1、获取到要设置的地址对象
        obj = self.get_object()
        obj.is_default = True
        obj.save()
        # 2、将该地址设置为默认收货地址，将用户的其他收货地址设置为非默认
        # 获取用户收货地址
        queryset = self.get_queryset().filter(user=request.user)
        for item in queryset:
            if item != obj:
                item.is_default = False
                item.save()
        return Response({"message": "设置成功"}, status=status.HTTP_200_OK)


class SendMSView(APIView):
    """发送短信验证码"""
    # 设置限流，每分钟只能获取一次
    throttle_classes = (AnonRateThrottle,)

    def post(self, request):
        # 获取手机号码
        mobile = request.data.get('mobile', '')
        # 验证手机号码格式是否正确（正则表达式匹配）
        res = re.match(r'^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$', mobile)
        if not res:
            return Response({'error': "无效的手机号码"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        # 随机生成一个验证码
        code = self.get_random_code()
        # 发送短信验证码
        result = AliyunMessage().send_msg(mobile, code)
        if result['code'] == 'OK':
            # 将短信验证码入库
            obj = VerifCode.objects.create(mobile=mobile, code=code)
            result['codeID'] = obj.id
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_random_code(self):
        # 随机生成一个6位数的验证码
        code = ''
        for i in range(6):
            # 随机生成0-9中的一个数据
            n = random.choice(range(10))
            code += str(n)
        return code


class AreaView(GenericViewSet, mixins.ListModelMixin):
    """省市区县数据查询接口"""
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    filterset_fields = ('level',)
