import deepdiff


def is_model_instance(val):
    """
    check whether val is model instance or not
    :param val: (object)
    :return:
        (bool) True - model instance, False - otherwise
        (str) error message
    """
    if not hasattr(val, 'fields'):
        return False, 'not exist field attribute'
    if not hasattr(val, 'to_dict'):
        return False, 'not exist to_dict method'

    return True, 'success'

def compare(obj1, obj2):
    """
    compare obj1 and obj2
    :param obj1: (object) compare object1
    :param obj2: (object) compare object2
    :return:
    (bool) True - same attributes bet/ self, obj, False - different
    (list) different attribute list
    :test:
    """
    ok, err = is_model_instance(obj1)
    if not ok:
        raise TypeError('Invalid model instance, obj1')
    ok, err = is_model_instance(obj2)
    if not ok:
        raise TypeError('Invalid model instance, obj2')
    if type(obj1) != type(obj2):
        raise TypeError('Different type comparison between obj1 and obj2')

    dict1 = obj1.to_dict()
    dict2 = obj2.to_dict()

    diff = deepdiff.DeepDiff(dict1, dict2)
    if len(diff) == 0:
        return True, []
    else:
        return False, diff.affected_root_keys.items

def update(obj1, obj2, attrs):
    """
    update model obj1 with obj2's attrs and value
    :param obj1: (object) model object1
    :param obj2: (object) model object2
    :param attrs: (list[str]) updated attributes(model's fields)
    :return:
    """
    ok, err = is_model_instance(obj1)
    if not ok:
        raise TypeError('Invalid model instance, obj1')
    ok, err = is_model_instance(obj2)
    if not ok:
        raise TypeError('Invalid model instance, obj2')
    if type(obj1) != type(obj2):
        raise TypeError('Different type comparison between obj1 and obj2')
    for attr in attrs:
        setattr(obj1, attr, getattr(obj2, attr))

# if __name__ == "__main__":
#     name = 'aa'
#     namespace = 'bb'
#     state = 'cc'
#     labels = []
#     host_ip = None
#     pod_ip = ''
#     node = ''
#     cond1 = Condition(condition='condition1',
#                       status='status',
#                       message='message1',
#                       updated='updated')
#     cond2 = Condition(condition='condition2',
#                       status='status',
#                       message='message2',
#                       updated='updated')
#
#     cond3 = Condition(condition='condition3',
#                       status='status',
#                       message='message3',
#                       updated='updated')
#     conditions1 = [ cond1, cond2 ]
#     conditions2 = [ cond2, cond1 ]
#     images = [ 'aa', 'bb', 'cc' ]
#     images2 = ['aa1', 'bb', 'cc']
#     stime = '123123'
#
#     pod1 = Pod(name=name,
#                namespace=namespace,
#                state=state,
#                labels=labels,
#                host_ip=host_ip,
#                pod_ip=pod_ip,
#                node=node,
#                conditions=conditions1,
#                images=images,
#                stime=stime)
#     pod2 = Pod(name=name,
#                namespace=namespace,
#                state=state,
#                labels=labels,
#                host_ip=host_ip,
#                pod_ip=pod_ip,
#                node=node,
#                conditions=conditions1,
#                images=images,
#                stime=stime)
#
#     compare(pod1, pod2)

