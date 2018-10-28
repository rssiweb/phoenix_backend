Vue.use(Toasted, {
    iconPack: 'fontawesome'
})

Vue.http.interceptors.push(function (request, next) {
    // modify request
    request.headers.set('Authorization', 'Bearer ' + this.token)

    // return response callback
    next(function (response) {
        // modify response
        if (response.status == 401) {
            this.$toasted.show(response.body.message, {
                theme: 'primary',
                className: "ui orange label",
                position: "bottom-right",
                singleton: true,
                icon: 'check',
                duration: 2000,
                onComplete: this.logout
            })
        }
    })
})

Vue.filter('capitalize', function (value) {
    if (!value) return ''
    value = value.toString()
    return value.charAt(0).toUpperCase() + value.slice(1)
})

var utils = {
    data: function () {
        return {
            token: Cookies.get('auth_token'),
            is_admin: (Cookies.get('is_admin') == 'true'),
            name: Cookies.get('name'),
            profile_image: Cookies.get('profile_image'),

            showModals: {},
            is_update_action: false,
        }
    },
    methods: {
        logout: function () {
            Cookies.remove('auth_token');
            window.location = '/';
        },
        getHeaders: function () {
            return {
                Authorization: 'Basic ' + this.token
            }
        },
        getBranchName(id) {
            if (this.branches) {
                var name = undefined
                this.branches.forEach(branch => {
                    if (id === branch.id) {
                        name = branch.name
                    }
                })
                return name
            } else {
                console.log('branches are not loaded')
            }
        },
        getCategoryName(id) {
            if (this.categories) {
                var name = undefined
                this.categories.forEach(cat => {
                    if (id == cat.id) {
                        name = cat.name
                    }
                })
                return name
            } else {
                console.log('categories are not loaded')
            }
        },
        showToast: function (message, type, faicon, indefinite) {
            // type info error warn
            var color = ''
            var icon = ''
            if (type == 'error') {
                color = 'red'
                icon = 'close'
            } else if (type == 'warn') {
                color = 'orange'
                icon = 'exlaimation'
            } else if (type == 'success') {
                color = 'olive'
                icon = 'check'
            } else if (type == 'info') {
                color = 'blue'
                icon = 'info'
            } else {
                console.log(type, 'is not a valid toast type')
                return
            }
            var duration = 3000
            if (indefinite) {
                duration = undefined
            }
            if (faicon) {
                icon = faicon
            }
            this.$toasted.clear()
            this.$toasted.show(message, {
                theme: 'primary',
                className: "ui " + color + " label",
                position: "bottom-right",
                singleton: true,
                icon: icon,
                duration: duration
            })
        },
        loadv2(items, callback) {
            // items is an array of loadConfigs 
            // loadConfig = {name, url, variableName, dataInReponse}
            // name- visible name to user in loading text 
            // url - url to hit a get request
            // variableName - save received data back in 
            // dataInReponse - reponse data present in this variable
            console.log('items', items)
            var vm = this
            var taskCount = items.length

            var receviedData = {}
            var names = []

            items.forEach(item => {
                names.push(item.name)
            })
            console.log(names)

            var errorMessage = undefined
            var errors = {}

            var updateLoadingMessage = function () {
                if (names.length > 0) {
                    suffix = names.join(', ')
                    vm.loading = 'loading ' + suffix + '...'
                } else
                    vm.loading = undefined
            }
            updateLoadingMessage() // set loading message

            var setAllToVm = function () {
                updateLoadingMessage()
                if (taskCount == 0) {
                    console.log('receviedData', receviedData)
                    if (errorMessage) {
                        vm.error = errorMessage
                    } else {
                        items.forEach(item => {
                            vm[item.variableName] = receviedData[item.dataInReponse] || item.default
                        })
                        vm.error = ''
                    }
                    vm.loading = undefined
                    console.log('done leading')
                    if (callback) {
                        callback()
                    }
                }
            }
            var showError = function () {
                updateLoadingMessage()
                var errored = []
                items.forEach(item => {
                    if (errors[item.name]) {
                        errored.push(item.name)
                    }
                })
                if (errored.length > 0) {
                    suffix = errored.join(', ')
                    errorMessage = 'Error occured in loading ' + suffix + ' please reload the page'
                }
                if (taskCount == 0) {
                    vm.error = errorMessage
                    vm.loading = undefined
                    console.log('done leading')
                }
            }

            var getErrorText = function (error) {
                if (error.body)
                    return error.body.message || error.statusText
                return error.statusText
            }

            items.forEach(item => {
                vm.$http.get(item.url)
                    .then(response => {
                            console.log(response)
                            taskCount -= 1
                            names.pop(names.indexOf(item.name))
                            if (response.body.status === 'success') {
                                receviedData[item.dataInReponse] = response.body[item.dataInReponse]
                            }
                            setAllToVm()
                        },
                        error => {
                            console.log(error)
                            taskCount -= 1
                            names.pop(names.indexOf(item.name))
                            errors[item.name] = getErrorText(error)
                            showError()
                        })
            })
        },
        constructErrorMessage(errorType, errorData) {
            var readableFieldNameMap = {
                dob: 'Date of Birth',
                name: 'Name',
                contact: 'Contact Number',
                category: 'Category',
                branch: 'Branch',
                id: 'Student ID',
            }
            if (errorType === 'BLANK_VALUES_FOR_REQUIRED_FIELDS') {
                // errorData is a list of values that are blank in a post/get request
                var readableFieldNames = []
                errorData.forEach((item, index) => {
                    var readableFieldName = readableFieldNameMap[item] || item
                    readableFieldNames.push(readableFieldName)
                })
                if (readableFieldNames.length > 0) {
                    var lastField = readableFieldNames.pop()
                    return readableFieldNames.join(', ') + ' and ' + lastField + ' values cannot be blank'
                } else {
                    console.log('received BLANK_VALUES_FOR_REQUIRED_FIELDS but with no field names')
                    return 'blank values for some fields'
                }
            } else if (errorType === 'DUPLICATE_ID') {
                console.log(errorData)
                var field = readableFieldNameMap[errorData[0]]
                var value = errorData[1]
                return 'Duplicate value "' + value + '" for field ' + field
            }
        },
        showCreateModal(modal_id, values) {
            console.log(modal_id)
            if (!modal_id) return
            var data = this.showModalSettings[modal_id]
            console.log(data)
            if(!data) return
            var modal_sel = data.modal_sel
            var form_sel = data.form_sel
            var defaults = values || data.defaults
            var pre = data.pre
            var post = data.post

            if (!modal_sel.startsWith('#') && !modal_sel.startsWith('.')) {
                modal_sel = '#' + modal_sel
            }
            if (!form_sel) form_sel = '.form'
            if (!form_sel.startsWith('#') && !form_sel.startsWith('.')) {
                form_sel = '#' + form_sel
            }
            var modal = $(modal_sel)
            var form = modal.find(form_sel)
            form.form('clear')
            form.form('set values', defaults) 
            if (typeof defaults == 'object') {
                form.form('set values', defaults)
            }
            this.is_update_action = false
            if(pre) pre()
            $(modal_sel).modal('show')
            if(post) post()
        },
        showUpdateModal(modal_id, item) {
            if (!modal_id) return
            var data = this.showModalSettings[modal_id]
            if(!data) return
            var values = $.extend({}, data.defaults, item)
            this.showCreateModal(modal_id, values)
            this.is_update_action = true
        },
        showModal: function (modalid) {
            if (!modalid) {
                console.log('Invalid modal ID:', modalid)
            }
            $('#' + modalid).modal('show')
        },
        getSubjectName: function (id) {
            var name = ''
            this.subjects.forEach((sub, index) => {
                if (sub.id === id) {
                    name = sub.name
                }
            })
            return name
        },
        getSubject: function (subId) {
            var subject = undefined
            subId = parseInt(subId)
            this.subjects.forEach((sub, index) => {
                if (sub.id === subId) {
                    subject = sub
                }
            })
            return subject
        },
        getFacultyName: function (facid) {
            var name = ''
            facid = parseInt(facid)
            this.faculties.forEach((fac, index) => {
                if (fac.id === facid) {
                    name = fac.name
                }
            })
            return name
        }
    }
}
