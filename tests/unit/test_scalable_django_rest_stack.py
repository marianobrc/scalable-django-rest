import aws_cdk as core
import aws_cdk.assertions as assertions

from scalable_django_rest.scalable_django_rest_stack import ScalableDjangoRestStack

# example tests. To run these tests, uncomment this file along with the example
# resource in scalable_django_rest/scalable_django_rest_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ScalableDjangoRestStack(app, "scalable-django-rest")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
