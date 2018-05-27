Vue.use(Toasted, {
    iconPack : 'fontawesome'
})

Vue.http.interceptors.push(function(request, next) {
  // modify request
  request.headers.set('Authorization', 'Bearer ' + this.token)

  // return response callback
  next(function(response) {
    // modify response
    if(response.status == 401){
        this.$toasted.show(response.body.message, {
            theme: 'primary',
            className: "ui orange label",
            position: "bottom-right",
            singleton: true,
            icon : 'check',
            duration : 2000,
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
    data: function(){
        return {
            token: Cookies.get('auth_token'),
            is_admin: (Cookies.get('is_admin')=='true'),
            name: Cookies.get('name')
        }
    },
    methods: {
        logout: function(){
            Cookies.remove('auth_token');
            window.location = '/';
        },
        getHeaders: function(){
            return { Authorization: 'Basic ' +  this.token}
        },
        getBranchName(id){
            if(this.branches){
                var name = undefined
                this.branches.forEach(branch => {
                    if(id === branch.id){
                        name = branch.name
                    }
                })
                return name
            }else{
                console.log('branches are not loaded')
            }
        },
        getCategoryName(id){
            if(this.categories){
                var name= undefined
                this.categories.forEach(cat => {
                    if(id == cat.id){
                        name = cat.name
                    }
                })
                return name
            }else{
                console.log('categories are not loaded')
            }  
        },
        showToast: function(message, type, faicon, indefinite){
            // type info error warn
            var color = ''
            var icon = ''
            if(type == 'error'){
                color = 'red'
                icon = 'close'
            }
            else if (type == 'warn'){
                color = 'orange'
                icon = 'exlaimation'
            }
            else if (type=='success'){
                color = 'olive'
                icon = 'check'
            }
            else if (type=='info'){
                color = 'blue'
                icon = 'info'
            }
            else{
                console.log(type, 'is not a valid toast type')
                return
            }
            var duration = 2000
            if (indefinite){
                duration = undefined
            }
            if(faicon){
                icon = faicon
            }
            this.$toasted.show(message, {
                theme: 'primary',
                className: "ui " + color + " label",
                position: "bottom-right",
                singleton: true,
                icon : icon,
                duration : duration
            })
        },
        load(items, callback){
            var possibleItems = ['branches', 'categories', 'faculties', 'students', 'allStudents', 'subjects', 'exams']
            var taskCount = 0
            var loadItems = {}
            possibleItems.forEach(item => {
                if(items.indexOf(item) != -1){
                    taskCount += 1
                    loadItems[item] = true
                }
            })

            if (loadItems.students && loadItems.allStudents){
                console.log('warning: do not pass students and allStudents both')
                loadItems.students = undefined
                taskCount -= 1
            }

            console.log('loading', taskCount, 'items', items, loadItems)
            var vm = this
            var branches = undefined
            var categories = undefined
            var students = undefined
            var faculties = undefined
            var subjects = undefined
            var exams = undefined

            var errorMessage = undefined
            var errors = {}

            var updateLoadingMessage = function(){
                if(items.length > 0){
                    suffix = items.join(', ')
                    suffix = suffix.replace(/\b\w/g, l => l.toUpperCase())
                    vm.loading = 'loading ' + suffix + '...'
                }
                else 
                    vm.loading = undefined
            }
            updateLoadingMessage() // set loading message

            var setAllToVm = function(){
                updateLoadingMessage()
                if(taskCount == 0){
                    if(errorMessage){
                        vm.error = errorMessage
                        vm.loading = undefined
                    }else{
                        if(loadItems.categories)
                            vm.categories = categories
                        if(loadItems.branches)
                            vm.branches = branches
                        if(loadItems.students || loadItems.allStudents)
                            vm.students = students
                        if(loadItems.faculties)
                            vm.faculties = faculties
                        if(loadItems.subjects)
                            vm.subjects = subjects
                        if(loadItems.exams)
                            vm.exams = exams
                    }
                    console.log('done leading')
                    if (callback) {
                        callback()
                    }
                }
            }

            var showError = function(){
                updateLoadingMessage()
                var errored = []
                possibleItems.forEach(item => {
                    if(errors[item]){
                        errored.push(item)
                    }
                })
                if (errored.length > 0){
                    suffix = errored.join(', ')
                    suffix = suffix.replace(/\b\w/g, l => l.toUpperCase())
                    errorMessage = 'Error occured in loading ' + suffix + ' please reload the page'
                }
                if(taskCount == 0){
                    vm.error = errorMessage
                    vm.loading = undefined
                    console.log('done leading')
                }
            }

            var getErrorText = function(error){
                if(error.body)
                    return error.body.message || error.statusText
                return error.statusText
            }

            if(loadItems.branches){
                this.$http.get('/api/branches')
                .then(response => {
                    taskCount -= 1
                    items.pop(items.indexOf('branches'))
                    if(response.body.status === 'success'){
                        branches = response.body.branches
                    }
                    setAllToVm()
                },
                error => {
                    console.log(error)
                    taskCount -= 1
                    items.pop(items.indexOf('branches'))
                    errors.branches = getErrorText(error)
                    showError()
                })
            }

            if(loadItems.categories){
                this.$http.get('/api/categories')
                .then(response => {
                    taskCount -= 1
                    items.pop(items.indexOf('categories'))
                    if(response.body.status === 'success'){
                        categories = response.body.categories
                    }
                    setAllToVm()
                },
                error => {
                    console.log(error)
                    taskCount -= 1
                    items.pop(items.indexOf('categories'))
                    errors.categories = getErrorText(error)
                    showError()
                })
            }

            if(loadItems.students || loadItems.allStudents){
                var url = '/api/student' + (loadItems.allStudents ? '/all': '')
                this.$http.get(url)
                .then(response => {
                    taskCount -= 1
                    items.pop(items.indexOf('students'))
                    if(response.body.status === 'Success'){
                        students = response.body.students
                    }
                    setAllToVm()
                },
                error => {
                    console.log(error)
                    taskCount -= 1
                    items.pop(items.indexOf('students'))
                    errors.students = getErrorText(error)
                    showError()
                })
            }

            if(loadItems.faculties){
                this.$http.get('/api/admin/faculties')
                .then(response => {
                    console.log(response)
                    taskCount -= 1
                    items.pop(items.indexOf('faculties'))
                    if(response.body.status === 'success'){
                        faculties = response.body.faculties
                    }
                    setAllToVm()
                },
                error => {
                    console.log(error)
                    taskCount -= 1
                    items.pop(items.indexOf('faculties'))
                    errors.faculties = getErrorText(error)
                    showError()
                })
            }

            if(loadItems.subjects){
                this.$http.get('/api/subject/list')
                .then(response => {
                    console.log(response)
                    taskCount -= 1
                    items.pop(items.indexOf('subjects'))
                    if(response.body.status === 'success'){
                        subjects = response.body.subjects
                    }
                    setAllToVm()
                },
                error => {
                    console.log(error)
                    taskCount -= 1
                    items.pop(items.indexOf('subjects'))
                    errors.subjects = getErrorText(error)
                    showError()
                })
            }

            if(loadItems.exams){
                this.$http.get('/api/exam/list')
                .then(response => {
                    console.log(response)
                    taskCount -= 1
                    items.pop(items.indexOf('exams'))
                    if(response.body.status === 'success'){
                        exams = response.body.exams
                    }
                    setAllToVm()
                },
                error => {
                    console.log(error)
                    taskCount -= 1
                    items.pop(items.indexOf('exams'))
                    errors.exams = getErrorText(error)
                    showError()
                })
            }

        },
        constructErrorMessage(errorType, errorData){
            var readableFieldNameMap = {
                dob: 'Date of Birth',
                name: 'Name',
                contact: 'Contact Number',
                category: 'Category',
                branch: 'Branch',
                id: 'Student ID',
            }
            if(errorType === 'BLANK_VALUES_FOR_REQUIRED_FIELDS'){
                // errorData is a list of values that are blank in a post/get request
                var readableFieldNames = []
                errorData.forEach((item, index) => {
                    var readableFieldName = readableFieldNameMap[item] || item
                    readableFieldNames.push(readableFieldName)
                })
                if (readableFieldNames.length > 0){
                    var lastField = readableFieldNames.pop()
                    return readableFieldNames.join(', ') + ' and ' + lastField + ' values cannot be blank'
                }
                else{
                    console.log('received BLANK_VALUES_FOR_REQUIRED_FIELDS but with no field names')
                    return 'blank values for some fields'
                }
            }
            else if (errorType === 'DUPLICATE_ID'){
                console.log(errorData)
                var field = readableFieldNameMap[errorData[0]]
                var value = errorData[1]
                return 'Duplicate value "'+value+'" for field '+field
            }
        },
        showModal: function(modalid){
            if(!modalid){
                console.log('Invalid modal ID:',modalid)
            }
            $('#' + modalid).modal('show')
        },
        getSubjectName: function(id){
            var name = ''
            this.subjects.forEach((sub, index)=>{
                if(sub.id === id){
                    name = sub.name
                }
            })
            return name
        }
    }
}
