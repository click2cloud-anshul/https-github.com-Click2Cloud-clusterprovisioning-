import ast
import json
import subprocess

import after_response
import docker
from django.http import JsonResponse
from rest_framework.decorators import api_view

from cluster.others.miscellaneous_operation import insert_or_update_s2i_details, get_s2i_details, \
    delete_s2i_image_detail_from_db
from cluster.others.miscellaneous_operation import key_validations_cluster_provisioning


@api_view(['POST'])
def create_new_image_using_s2i(request):
    """
    This method creates the new image using s2i
    :param request: parameters passed during the api call
    :return:
    """

    api_response = {'is_successful': False,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'registry_username', 'registry_password', 'github_url', 'builder_image',
                           'image_name', 'tag', 'registry']
        error, response = key_validations_cluster_provisioning(json_request, valid_json_keys)
        if error:
            api_response.update({
                'error': response.get('error')
            })
        else:
            github_username = ''
            github_password = ''
            if 'github_username' in json_request and 'github_password' in json_request:
                github_username = json_request.get('github_username')
                github_password = json_request.get('github_password')

            rm_https_from_giturl = json_request.get('github_url').strip().lstrip('https://')
            check_github_repo = subprocess.Popen(
                ['git', 'ls-remote', 'https://%s:%s@%s' % (github_username, github_password, rm_https_from_giturl)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = check_github_repo.communicate()

            if error != '':
                split_error_string = error.split('\n')
                partition_error_string = split_error_string[0].partition('remote: ')[2]
                if partition_error_string == '':
                    api_response.update({
                        'error': 'github repository not found.'
                    })
                else:
                    api_response.update({
                        'error': 'github %s' % (partition_error_string).lower()
                    })
            else:
                create_new_image_operation.after_response(json_request)
                api_response.update({
                    'is_successful': True
                })
    except Exception as e:
        api_response.update({
            'error': e.message
        })
    finally:
        return JsonResponse(api_response, safe=False)


# @api_view(['POST'])
# def create_application(request):
#     """
#     This method creates the new application using s2i and deploy on kubernetes
#     :param request: parameters passed during the api call
#     :return:
#     """
#
#     api_response = {'is_successful': False,
#                     'error': None}
#     try:
#         json_request = json.loads(request.body)
#         valid_json_keys = ['user_id', 'provider_id', 'cluster_id', 'application_name', 'build_config',
#                            'deployment_config']
#         error, response = key_validations_cluster_provisioning(json_request, valid_json_keys)
#         if error:
#             api_response.update({
#                 'error': response.get('error')
#             })
#         else:
#             # github_username = ''
#             # github_password = ''
#             # if 'github_username' in json_request and 'github_password' in json_request:
#             #     github_username = json_request.get('github_username')
#             #     github_password = json_request.get('github_password')
#             #
#             # rm_https_from_giturl = json_request.get('github_url').strip().lstrip('https://')
#             # check_github_repo = subprocess.Popen(
#             #     ['git', 'ls-remote', 'https://%s:%s@%s' % (github_username, github_password, rm_https_from_giturl)],
#             #     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#             # output, error = check_github_repo.communicate()
#             #
#             # if error != '':
#             #     split_error_string = error.split('\n')
#             #     partition_error_string = split_error_string[0].partition('remote: ')[2]
#             #     if partition_error_string == '':
#             #         api_response.update({
#             #             'error': 'github repository not found.'
#             #         })
#             #     else:
#             #         api_response.update({
#             #             'error': 'github %s' % (partition_error_string).lower()
#             #         })
#             # else:
#
#             create_new_application_operation.after_response(json_request)
#             api_response.update({
#                 'is_successful': True
#             })
#     except Exception as e:
#         api_response.update({
#             'error': e.message
#         })
#     finally:
#         return JsonResponse(api_response, safe=False)
#

def delete_builder_image(docker_cli, builder_image):
    """
    This function will delete the builder image from docker
    :param docker_cli:
    :param builder_image:
    :return:
    """
    error = False
    response = None
    try:
        get_pull_images = docker_cli.images(builder_image)
        if get_pull_images != []:
            remove_pull_image = docker_cli.remove_image(builder_image)
    except Exception as e:
        error = True
        response = e.message
    finally:
        return error, response


def delete_new_image(docker_cli, new_image):
    """
    This function will delete the builder image from docker
    :param docker_cli:
    :param new_image:
    :return:
    """
    error = False
    response = None
    try:
        get_pull_images = docker_cli.images(new_image)
        if get_pull_images != []:
            remove_pull_image = docker_cli.remove_image(new_image)
    except Exception as e:
        error = True
        response = e.message
    finally:
        return error, response


def delete_tag_image(docker_cli, tag_image):
    """
    This function will delete the builder image from docker
    :param docker_cli:
    :param tag_image:
    :return:
    """
    error = False
    response = None
    try:
        get_pull_images = docker_cli.images(tag_image)
        if get_pull_images != []:
            remove_pull_image = docker_cli.remove_image(tag_image)
    except Exception as e:
        error = True
        response = e.message
    finally:
        return error, response


def after_response_create_image(json_request):
    """
    create the new image using s2i in after response
    :param json_request:
    :return:
    """
    record_unique_id = ''
    try:
        # docker_version = subprocess.Popen(
        #     ['docker', 'version'],
        #     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # output, info = docker_version.communicate()
        # print "output \n %s" % output
        # print "info \n %s" % info
        dockercli = docker.APIClient()
        github_username = ''
        github_password = ''
        registry_username = json_request.get('registry_username')
        registry_password = json_request.get('registry_password')

        if 'github_username' in json_request:
            github_username = json_request.get('github_username')

        if 'github_password' in json_request:
            github_password = json_request.get('github_password')

        github_url = json_request.get('github_url')
        builder_image = json_request.get('builder_image')
        new_image_name = json_request.get('image_name')

        registry = ''
        if 'docker.io' in json_request.get('registry'):
            registry = '%s/%s' % (registry_username, new_image_name)
        else:
            registry = '%s/%s' % (json_request.get('registry'), new_image_name)

        tag = json_request.get('tag')
        auth_config = {'username': registry_username, 'password': registry_password}

        json_request['is_insert'] = True
        json_request['status'] = 'In-Progress'
        json_request['comment'] = 'Image is in build state'
        insert_response, error = insert_or_update_s2i_details(json_request)

        record_unique_id = insert_response[0][0]

        rm_https_from_giturl = github_url.strip().lstrip('https://')

        build_new_image = subprocess.Popen(
            ['s2i', 'build', 'https://%s:%s@%s' % (github_username, github_password, rm_https_from_giturl),
             builder_image, new_image_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, info = build_new_image.communicate()

        if 'Build completed successfully' not in info:

            json_request.update({'is_insert': False,
                                 'status': 'Failed',
                                 'comment': 'Error while building the new image'})
            insert_response, error = insert_or_update_s2i_details(json_request, record_unique_id)

            print insert_response

            if error:
                json_request.update({'is_insert': False,
                                     'status': 'Failed',
                                     'comment': 'Error while updating the data'})
                insert_or_update_s2i_details(json_request, record_unique_id)
            # error, response = delete_builder_image(dockercli, builder_image)
            # if error:
            #     json_request.update({'is_insert': False,
            #                          'status': 'Failed',
            #                          'comment': 'Error while deleting the builder image'})
            #     insert_or_update_s2i_details(json_request, record_unique_id)
        else:
            json_request.update({'is_insert': False,
                                 'status': 'In-Progress',
                                 'comment': 'Build completed successfully'})
            insert_or_update_s2i_details(json_request, record_unique_id)
            tag_image = dockercli.tag(image=new_image_name, repository=registry, tag=tag)

            if not tag_image:
                json_request.update({'is_insert': False,
                                     'status': 'Failed',
                                     'comment': 'Error while tagging the image'})
                insert_or_update_s2i_details(json_request, record_unique_id)
                # error, response = delete_builder_image(dockercli, builder_image)
                # if error:
                #     json_request.update({'is_insert': False,
                #                          'status': 'Failed',
                #                          'comment': 'Error while deleting the builder image'})
                #     insert_or_update_s2i_details(json_request, record_unique_id)

                error, response = delete_new_image(dockercli, new_image_name)
                if error:
                    json_request.update({'is_insert': False,
                                         'status': 'Failed',
                                         'comment': 'Error while deleting the new image'})
                    insert_or_update_s2i_details(json_request, record_unique_id)
            else:
                json_request.update({'is_insert': False,
                                     'status': 'In-Progress',
                                     'comment': 'Image has been tagged'})
                insert_or_update_s2i_details(json_request, record_unique_id)

                push_image = dockercli.push(repository=registry, tag=tag, auth_config=auth_config)

                if 'errorDetail' in push_image:
                    error_partition = push_image.partition('"errorDetail":')[2]
                    join_string = '{"errorDetail":%s' % error_partition
                    res = ast.literal_eval(join_string)
                    comment = ''
                    if 'errorDetail' in res:
                        if 'message' in res.get('errorDetail'):
                            comment = 'docker push error: %s' % (res.get('errorDetail').get('message'))
                        else:
                            # user defined message
                            comment = 'Error while pushing new images'
                    else:
                        # user defined message
                        comment = 'Error while pushing new images'

                    json_request.update({'is_insert': False,
                                         'status': 'Failed',
                                         'comment': comment})
                    insert_or_update_s2i_details(json_request, record_unique_id)

                    # error, response = delete_builder_image(dockercli, builder_image)
                    # if error:
                    #     json_request.update({'is_insert': False,
                    #                          'status': 'Failed',
                    #                          'comment': 'Error while deleting the builder image'})
                    #     insert_or_update_s2i_details(json_request, record_unique_id)

                    error, response = delete_new_image(dockercli, new_image_name)
                    if error:
                        json_request.update({'is_insert': False,
                                             'status': 'Failed',
                                             'comment': 'Error while deleting the new image'})
                        insert_or_update_s2i_details(json_request, record_unique_id)

                    error, response = delete_tag_image(dockercli, '%s:%s' % (registry, tag))
                    if error:
                        json_request.update({'is_insert': False,
                                             'status': 'Failed',
                                             'comment': 'Error while deleting the tag image'})
                        insert_or_update_s2i_details(json_request, record_unique_id)

                else:

                    json_request.update({'is_insert': False,
                                         'status': 'In-Progress',
                                         'comment': 'Image has been pushed'})
                    insert_or_update_s2i_details(json_request, record_unique_id)

                    error, response = delete_new_image(dockercli, new_image_name)
                    if error:
                        json_request.update({'is_insert': False,
                                             'status': 'Failed',
                                             'comment': 'Error while deleting the new image'})
                        insert_or_update_s2i_details(json_request, record_unique_id)

                    error, response = delete_tag_image(dockercli, '%s:%s' % (registry, tag))
                    if error:
                        json_request.update({'is_insert': False,
                                             'status': 'Failed',
                                             'comment': 'Error while deleting the tag image'})
                        insert_or_update_s2i_details(json_request, record_unique_id)

                    # error, response = delete_builder_image(dockercli, builder_image)
                    # if error:
                    #     json_request.update({'is_insert': False,
                    #                          'status': 'Failed',
                    #                          'comment': 'Error while deleting the builder image'})
                    #     insert_or_update_s2i_details(json_request, record_unique_id)

                    json_request.update({'is_insert': False,
                                         'status': 'Completed',
                                         'comment': 'New image created successfully'})
                    insert_or_update_s2i_details(json_request, record_unique_id)

    except Exception as e:
        json_request.update({'is_insert': False,
                             'status': 'Failed',
                             'comment': e.message})
        insert_or_update_s2i_details(json_request, record_unique_id)


@after_response.enable
def create_new_image_operation(json_request):
    """
    create the new image using s2i in after response
    :param json_request:
    :return:
    """
    try:
        after_response_create_image(json_request)
    except Exception as e:
        print e.message


@after_response.enable
def create_new_application_operation(json_request):
    """
    create the new image using s2i in after response
    :param json_request:
    :return:
    """
    try:
        after_response_create_image(json_request)
    except Exception as e:
        print e.message


@api_view(['GET'])
def get_image_details(request):
    """
    get the list of the s2i images
    :param request:
    :return:
    """
    api_response = {'is_successful': False,
                    'image_list': [],
                    'error': None}
    try:

        if request.GET.get('user_id'):
            error, record_list = get_s2i_details(request.GET['user_id'])
            if not error:
                image_detail_list = []
                if record_list is not None:
                    if len(list(record_list)) > 0:
                        for record in record_list:
                            image_detail = {'created_at': record[2],
                                            'image_name': record[3],
                                            'builder_image': record[4],
                                            'github_url': record[5],
                                            'tag': record[6],
                                            'status': record[7],
                                            'comments': record[8],
                                            'registry': record[9],
                                            }
                            image_detail_list.append(image_detail)
                    api_response.update({
                        'is_successful': True,
                        'image_list': image_detail_list,
                    })
            else:
                raise Exception(record_list)
        else:
            api_response.update({
                'error': 'query parameter user_id is not found'
            })
    except Exception as e:
        api_response.update({
            'error': e.message
        })
    finally:
        return JsonResponse(api_response, safe=False)


@api_view(['DELETE'])
def delete_image_detail(request):
    """
    delete the s2i image from database
    :param request:
    :return:
    """
    api_response = {'is_successful': False,
                    'error': None}
    try:
        json_request = json.loads(request.body)
        valid_json_keys = ['user_id', 'image_name', 'builder_image', 'tag', 'created_at', 'registry', 'github_url']
        error, response = key_validations_cluster_provisioning(json_request, valid_json_keys)
        if error:
            api_response.update({
                'error': response.get('error')
            })
        else:
            error, response = delete_s2i_image_detail_from_db(json_request)
            if not error:
                api_response.update({
                    'is_successful': True
                })
            else:
                raise Exception(response)
    except Exception as e:
        api_response.update({
            'error': e.message
        })
    finally:
        return JsonResponse(api_response, safe=False)
