import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
from django_tables2 import tables, SingleTableView, RequestConfig

from workline.harness_tools.harness_for_web import harness_testcase

from .models import Testbed, Testcase, Result, Suspicious_Result
from .tables import TestbedTable


def show_testcase(request):
    Testcase_id = request.GET.get('id')
    if not Testcase_id:
        Testcase_id = 1
    # print(Testcase_id)
    all_testcase = Testcase.objects.filter(id=Testcase_id)
    testcase_result = Result.objects.filter(Testcase_id=Testcase_id)
    all_suspicious_result = Suspicious_Result.objects.filter(Testcase_id=Testcase_id)

    remark = request.POST.get('remark')
    all_suspicious_result.update(Remark=remark)

    print(remark)

    return render(request, 'testcase.html', locals())


def harness(request):
    Testcase_id = request.GET.get('id')
    if not Testcase_id:
        Testcase_id = 1
    print(Testcase_id)

    all_testcase = Testcase.objects.filter(id=Testcase_id)

    # testcase = [all_testcase.first().id,
    #             all_testcase.first().Testcase_context,
    #             all_testcase.first().SourceFun_id,
    #             all_testcase.first().SourceTestcase_id,
    #             all_testcase.first().Fuzzing_times,
    #             all_testcase.first().Mutation_method,
    #             all_testcase.first().Mutation_times,
    #             all_testcase.first().Interesting_times,
    #             all_testcase.first().Probability,
    #             all_testcase.first().Remark]

    # Testcase_context = testcase[1]
    Testcase_context = all_testcase.first().Testcase_context

    return render(request, 'harness.html', locals())


def herness_ajax(request):
    herness_ajax = request.POST.get("herness_ajax")
    testcase_id = request.POST.get("Testcase_id")
    # print(herness_ajax)
    # print(testcase_id)

    all_testcase = Testcase.objects.filter(id=testcase_id)
    testcase = {'id': all_testcase.first().id,
                # 'Testcase_context': herness_ajax,
                'Testcase_context': bytes(herness_ajax, encoding="utf8"),
                'SourceFun_id': all_testcase.first().SourceFun_id,
                'SourceTestcase_id': all_testcase.first().SourceTestcase_id,
                'Fuzzing_times': all_testcase.first().Fuzzing_times,
                'Mutation_method': all_testcase.first().Mutation_method,
                'Mutation_times': all_testcase.first().Mutation_times,
                'Interesting_times': all_testcase.first().Interesting_times,
                'Engine_coverage': all_testcase.first().Engine_coverage,
                'Engine_coverage_integration_source': all_testcase.first().Engine_coverage_integration_source,
                'Engine_coverage_integration_all': all_testcase.first().Engine_coverage_integration_all,
                'Probability': all_testcase.first().Probability,
                'Remark': all_testcase.first().Remark}
    # testcase['Testcase_context'] = all_testcase.first().Testcase_context
    # print(testcase)

    dic = {}
    try:
        harness_result, different_result_list = harness_testcase(testcase)

        def obj_different_result_2_json(obj):
            return {
                'testcase_id': obj.testcase_id,
                "error_type": obj.error_type,
                "testbed_id": obj.testbed_id,
            }

        different_result_list = json.dumps(different_result_list, default=obj_different_result_2_json)
        dic = {'harness_result': str(harness_result), 'different_result_list': different_result_list}
        dic = json.dumps(dic)
        # print(dic)

    except:
        pass
    return HttpResponse(dic)

    # print(dic)

    # return HttpResponse(harness_result, different_result_list)

    # return HttpResponse(harness_result)


def remark_ajax(request):
    remark_ajax = request.POST.get("remark_ajax")
    testcase_id = request.POST.get("Testcase_id")

    all_suspicious_result = Suspicious_Result.objects.filter(Testcase_id=testcase_id)

    all_suspicious_result.update(Remark=remark_ajax)

    return HttpResponse("remark保存成功")


def get_remark_ajax(request):
    testcase_id = request.POST.get("Testcase_id")

    all_suspicious_result = Suspicious_Result.objects.filter(Testcase_id=testcase_id)
    dic = {}
    if all_suspicious_result:
        now_remark: str = all_suspicious_result.first().Remark
        dic['hasRemark'] = True
        dic['remarkContent'] = now_remark
    else:
        dic['hasRemark'] = False
    dic = json.dumps(dic)
    # print(dic)
    return HttpResponse(dic)


class testbed(SingleTableView):
    model = Testbed
    table_class = TestbedTable
    template_name = 'testbed.html'
