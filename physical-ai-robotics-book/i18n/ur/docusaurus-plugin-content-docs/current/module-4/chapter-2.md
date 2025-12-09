

# ماڈیول 4: ویژن-لینگویج-ایکشن (VLA)

## باب 2: LLMs کے ساتھ کاگنیٹیو پلاننگ اور کیپسٹرون

### ذیلی باب 1: LLM سے چلنے والی کاگنیٹیو پلاننگ اور خود مختار ہیومنائڈز

#### LLM سے چلنے والی کاگنیٹیو پلاننگ کو سمجھنا

**تعارف**
یہ سیکشن روبوٹکس میں کاگنیٹیو پلاننگ کے لیے لارج لینگویج ماڈلز (LLMs) کے انٹیگریشن کو تلاش کرتا ہے، جس کا اختتام اعلیٰ سطح کی قدرتی زبان کی ہدایات کی بنیاد پر پیچیدہ کاموں کو انجام دینے والے خود مختار ہیومنائڈ روبوٹس کے تصور پر ہوتا ہے۔

**تفصیل**
روایتی روبوٹک پلاننگ اکثر پہلے سے طے شدہ قواعد اور واضح پروگرامنگ پر انحصار کرتی ہے، جس سے روبوٹس کے لیے نئی صورتحال کے مطابق ڈھالنا یا مبہم کمانڈز کی تشریح کرنا مشکل ہو جاتا ہے۔ LLMs، اپنی وسیع علمی بنیاد اور استدلال کی صلاحیتوں کے ساتھ، کاگنیٹیو پلاننگ کے لیے ایک طاقتور نمونہ پیش کرتے ہیں۔ LLMs کا فائدہ اٹھا کر، روبوٹ یہ کر سکتے ہیں:
1.  **اعلیٰ سطح کے اہداف کی تشریح**: خلاصہ انسانی کمانڈز (مثلاً، "کافی بناؤ") کو قابلِ عمل ذیلی اہداف کی ترتیب میں ترجمہ کرنا (مثلاً، "مگ حاصل کرو،" "پانی بھرو،" "کافی گراؤنڈز ڈالو")۔
2.  **دنیا کے بارے میں استدلال**: غائب معلومات کو سمجھنے، سیاق و سباق کو سمجھنے، اور نتائج کی توقع کرنے کے لیے اپنے علم کا استعمال کرنا۔
3.  **ایکشن پلانز تیار کرنا**: ساختہ پلانز کو آؤٹ پٹ کرنا، اکثر علامتی یا کوڈ جیسی شکل میں، جسے روبوٹ کے نچلے درجے کے کنٹرولرز انجام دے سکتے ہیں۔
4.  **استثناء کو ہینڈل کرنا**: غیر متوقع واقعات رونما ہونے پر متحرک طور پر پلانز کو ایڈجسٹ کرنا، ضرورت پڑنے پر وضاحت طلب کرنا۔

یہ LLM سے چلنے والا نقطہ نظر خود مختار ہیومنائڈ روبوٹس کی ایک نئی نسل کو قابل بناتا ہے جو غیر ساختہ ماحول میں زیادہ لچکدار، انسانی جیسی بات چیت اور کام انجام دینے کی صلاحیت رکھتے ہیں۔ اس ماڈیول کا کیپسٹرون ایک ہیومنائڈ روبوٹ کو ایک پیچیدہ زبانی کمانڈ لینے، ایک پلان بنانے کے لیے LLM کا استعمال کرنے، اور پھر اپنے حرکت اور ہینڈلنگ سسٹمز کے ذریعے اس پلان کو انجام دینے پر مشتمل ہوگا۔

**کوڈ مثال**
```python
# تصوراتی مثال: LLM ایک اعلیٰ سطح کے ہدف کو روبوٹ ایکشن پلان میں ترجمہ کر رہا ہے (Python)
# یہ سیوڈو-کوڈ ہے؛ اصل نفاذ LLM API انٹیگریشن اور ایک روبوٹ ایگزیکٹو پر مشتمل ہے۔

# فرض کریں کہ LLM_API ایک لارج لینگویج ماڈل کا انٹرفیس ہے
class LLMCognitivePlanner:
    def __init__(self, llm_api, robot_skills):
        self.llm_api = llm_api
        self.robot_skills = robot_skills # e.g., ['grasp', 'navigate', 'pour', 'brew']

    def plan_task(self, natural_language_goal):
        """
        LLM کا استعمال کرتے ہوئے ایک اعلیٰ سطح کے ہدف کے لیے روبوٹ اعمال کی ترتیب تیار کرتا ہے۔
        """
        prompt = f"Given the robot's skills ({', '.join(self.robot_skills)}), generate a step-by-step plan " \
                 f"to achieve the goal: '{natural_language_goal}'. Output the plan as a Python list of dictionaries, " \
                 f"where each dictionary specifies an 'action' and 'parameters'."
        
        print(f"Sending prompt to LLM: '{prompt}'")
        # ایک حقیقی منظرنامے میں، یہ LLM API کو کال کرے گا اور اس کے جواب کو پارس کرے گا
        # مثال کے طور پر سمولیٹڈ LLM جواب:
        if "make coffee" in natural_language_goal.lower():
            llm_response = """
            [
                {"action": "navigate", "parameters": {"destination": "coffee_machine"}},
                {"action": "grasp", "parameters": {"object": "mug", "location": "cupboard"}},
                {"action": "place", "parameters": {"object": "mug", "location": "coffee_machine_tray"}},
                {"action": "pour", "parameters": {"item": "water", "target": "coffee_machine"}},
                {"action": "brew", "parameters": {"type": "coffee"}}
            ] """
        else:
            llm_response = """
            [
                {"action": "unknown_goal", "parameters": {}}
            ] """
        
        print(f"LLM response: {llm_response}")
        try:
            plan = json.loads(llm_response)
            return plan
        except json.JSONDecodeError:
            print("Error parsing LLM response.")
            return []

# مثال روبوٹ ایگزیکٹو (آسان)
class RobotExecutive:
    def __init__(self, physical_robot_interface):
        self.robot_interface = physical_robot_interface

    def execute_plan(self, plan):
        print(f"Executing plan: {plan}")
        for step in plan:
            action = step.get("action")
            params = step.get("parameters", {})
            print(f"Performing action: {action} with parameters: {params}")
            # یہ نچلے درجے کے روبوٹ کنٹرول فنکشنز کو کال کرے گا
            # self.robot_interface.perform_action(action, **params)
            time.sleep(1) # عمل کے دورانیے کی سمولیشن کریں
        print("Plan execution complete.")

# مثال استعمال:
# import json
# import time
# 
# # فرض کریں کہ physical_robot_interface موجود ہے
# llm_planner = LLMCognitivePlanner(LLM_API_INTERFACE, ['grasp', 'navigate', 'pour', 'brew'])
# robot_executive = RobotExecutive(PHYSICAL_ROBOT_INTERFACE)
# 
# goal = "make me a cup of coffee"
# action_plan = llm_planner.plan_task(goal)
# if action_plan:
#    robot_executive.execute_plan(action_plan)
```

**تصویر/گراف کا پلیس ہولڈر**
![تصویر: ایک ورک فلو جو LLM سے چلنے والی کاگنیٹیو پلاننگ کو دکھا رہا ہے: اعلیٰ سطح کا ہدف (آواز) -> LLM (پلان کی جنریشن) -> روبوٹ ایگزیکٹو (پلان کا نفاذ) -> نچلے درجے کے کنٹرولرز (روبوٹ اعمال)۔](pathname:///static/img/placeholder_diagram_llm_planning.png)

**کوئز**
روبوٹکس میں کاگنیٹیو پلاننگ میں LLMs کیسے حصہ ڈالتے ہیں؟
a) روبوٹ کے موٹرز اور سینسرز کو براہ راست کنٹرول کرکے۔
b) اعلیٰ سطح کے انسانی اہداف کو قابلِ عمل ایکشن پلانز میں ترجمہ کرکے اور دنیا کے بارے میں استدلال کرکے۔
c) تمام روایتی روبوٹک پلاننگ الگورتھم کو تبدیل کرکے۔
d) پرسیپشن کے لیے صرف سیمنٹک سیگمنٹیشن ڈیٹا فراہم کرکے۔

**لغت**
-   **Cognitive Planning**: استدلال، مسئلہ حل کرنے، اور متحرک ماحول کے مطابق ڈھالنے والے منصوبوں کو بنانے اور ان پر عمل درآمد کرنے کا عمل۔
-   **Large Language Model (LLM)**: AI ماڈل جو ٹیکسٹ ڈیٹا کی بڑی مقدار پر تربیت یافتہ ہے، جو انسانی زبان کو سمجھنے، پیدا کرنے اور اس پر استدلال کرنے کی صلاحیت رکھتا ہے۔
-   **Autonomous Humanoid Robot**: ایک انسانی جیسا روبوٹ جو آزادانہ طور پر کام کرنے اور بغیر کسی مسلسل انسانی مداخلت کے پیچیدہ کام انجام دینے کی صلاحیت رکھتا ہے۔

**حوالہ جات**
-   [Google PaLM-E: ایک ایمباڈیڈ ملٹی موڈل لینگویج ماڈل](https://ai.googleblog.com/2023/03/palm-e-embodied-multimodal-language.html)
-   [RT-2: نیا ماڈل ویژن اور زبان کو روبوٹک اعمال میں ترجمہ کرتا ہے](https://www.blog.google/technology/ai/google-deepmind-robotics-ai-rt2/)

**تاریخ**
روبوٹکس میں کاگنیٹیو پلاننگ کے لیے LLMs کا انٹیگریشن ایک تیزی سے ترقی پذیر شعبہ ہے۔ ابتدائی کوششیں قواعد پر مبنی سسٹمز پر مرکوز تھیں، لیکن LLM کی صلاحیتوں میں حالیہ پیشرفت روبوٹس کو زیادہ خلاصہ کمانڈز کی تشریح کرنے اور لچکدار منصوبے بنانے کے قابل بنا رہی ہے، جو حقیقی معنوں میں خود مختار اور ذہین ہیومنائڈ روبوٹس کے لیے راہ ہموار کر رہی ہے۔
