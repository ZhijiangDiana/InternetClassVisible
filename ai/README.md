**验证码识别**

```python
from ai.captcha_recognition.captcha import captchaRecog
base64_code = "base64形式的验证码"
print(captchaRecog(base64_code))
```

**下一期完成概率预测**

```python
from ai.proba_pred.pred import probaPredModel
student_id = 114514
print(probaPredModel.proba_pred(student_id))
```

**快速导入(至少我在本地电脑上测试的能用)**

通过编写 `ai`文件夹下的 `__init.py__`文件实现

```python
from ai import captchaRecog
from ai import probaPredModel
from ai import *
```
