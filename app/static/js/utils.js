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
        load(items, callback){
            var possibleItems = ['branches', 'categories', 'faculties', 'students', 'allStudents']
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
                        vm.categories = categories
                        vm.branches = branches
                        vm.students = students
                        vm.faculties = faculties
                    }
                    console.log('done leading')
                    if (callback) callback()
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
                    if(response.body.status === 'Success'){
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
        },
        constructErrorMessage(errorType, errorData){
            var readableFieldNameMap = {
                dob: 'Date of Birth',
                name: 'Name',
                contact: 'Contact Number',
                category: 'Category',
                branch: 'Branch'
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
        }
    }
}
