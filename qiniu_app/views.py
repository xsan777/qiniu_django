from django.shortcuts import render, HttpResponse
import qiniu
import json
from qiniu_app.qiniu_config import qiniu_config


# 七牛身份验证
def qiniu_auth():
    access_key = qiniu_config['access_key']
    secret_key = qiniu_config['secret_key']
    q = qiniu.Auth(access_key, secret_key)
    return q


# Create your views here.
# 将上传处理后的图片刷新到cdn节点，减少回源流量
def cdn_flush(key):
    auth = qiniu_auth()
    cdn_manager = qiniu.CdnManager(auth)
    domine = qiniu_config['domine']
    need_flush_url = domine + key
    # 需要刷新的文件链接
    urls = [
        need_flush_url,
    ]
    # URL刷新链接
    refresh_url_result = cdn_manager.refresh_urls(urls)
    return


# 进行上传的图片处理
def dealwith_img(request):
    q = qiniu_auth()
    key = request.GET.get('key')
    bucket_name = qiniu_config['bucket_name']
    # pipeline是使用的队列名称,不设置代表不使用私有队列，使用公有队列。
    # pipeline = 'your_pipeline'
    # 要进行的转换格式操作。
    fops = 'imageView2/0/format/webp/interlace/1'
    # 可以对缩略后的文件进行使用saveas参数自定义命名，当然也可以不指定文件会默认命名并保存在当前空间
    saveas_key = qiniu.urlsafe_base64_encode(bucket_name + ':' + key)
    fops = fops + '|saveas/' + saveas_key
    # pfop = qiniu.PersistentFop(q, bucket_name, pipeline)
    pfop = qiniu.PersistentFop(q, bucket_name)
    ops = []
    ops.append(fops)
    ret, info = pfop.execute(key, ops, 1)
    assert ret['persistentId'] is not None
    cdn_flush(key)
    return HttpResponse(json.dumps('ok'))


# 获取七牛上传的token
def qntoken(request):
    q = qiniu_auth()
    key = request.GET.get('key')
    bucket = qiniu_config['bucket_name']
    token = q.upload_token(bucket, key)
    return HttpResponse(json.dumps({'token': token}))


def qiniu_test(request):
    return render(request, 'qiniu_test.html')
