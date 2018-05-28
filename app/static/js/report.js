var app = new Vue({
    mixins: [utils],
    el: '#app',
    data: {
        branches: [],
        categories: [],
        students: [],
        selectedCategories: [],
        selectedBranches: [],
        selectedStudents: [],
        month: moment().format('DD MMMM YYYY'),
        loading: false,
        taskCount: 0,
        error: '',

        initialized: false,

        summaryMonthInitData: {
            type: 'month',
            closable: true,
            maxDate: new Date(),
            onChange: function(date, text, mode){
                return app.setMonth(date, text, mode)
            },
        },
        detailStartMonthInitData: {
            type: 'date',
            closable: true,
            maxDate: new Date(),
            onChange: function(date, text, mode){
                $('#detailEndMonth').calendar('set startDate', date)
                return app.setMonth(date, text, mode)
            },
        },
        detailEndMonthInitData: {
            type: 'date',
            closable: true,
            maxDate: new Date(),
            onChange: function(date, text, mode){
                return app.setEndMonth(date, text, mode)
            },
        },
        summaryReportModalInit: {
            onShow: function(){
                $('#summaryMonth').calendar(app.summaryMonthInitData)
            }
        },
        detailReportModalInit: {
            onShow: function(){
                $('#detailStartMonth').calendar(app.detailStartMonthInitData)
                $('#detailEndMonth').calendar(app.detailEndMonthInitData)
            }
        }
    },
    created(){
        console.log('created')
        this.loadv2([
            {name:'Categories',
             url:'/api/category/1/list',
             variableName: 'categories',
             dataInReponse: 'categories'},
            {name:'Branches',
             url:'/api/branch/list',
             variableName: 'branches',
             dataInReponse: 'branches'},
            {name:'Students',
             url: '/api/student/' + this.month.replace(/ /g,'') + '/all',
             variableName: 'students',
             dataInReponse: 'students'},
             ])
    },
    updated(){
        console.log('updated')
        if(!this.initialized && !this.loading){
            console.log('initialized')
            var dom = $(this.$el)
            dom.find('table').tablesort()
            dom.find('.dropdown').dropdown()
            dom.find('#month').calendar(this.monthInitData)
            dom.find('#summaryReportModal').modal(this.summaryReportModalInit)
            dom.find('#detailReportModal').modal(this.detailReportModalInit)
            this.initialized = true
        }
    },
    watch: {
        month(){
            console.log('fetch students', this.month)
            this.loadv2([
                {name:'Students',
                 url: '/api/student/' + this.month.replace(/ /g,'') + '/all',
                 variableName: 'students',
                 dataInReponse: 'students'},
                ])
        }
    },
    methods: {
        toggleStudentSelection(student){
            var index = this.selectedStudents.indexOf(student)
            if(index ==-1){
                this.selectedStudents.push(student)
            } else {
                this.selectedStudents.splice(index, 1)
            }
        },
        setMonth(date, text, mode){
            this.month = moment(date).format('DD MMMM YYYY')
            console.log('setting month', this.month)
        },
        setEndMonth: function(date, text, mode){
            console.log('end date set to', date)
        },
        exportReport(){
            this.loading = true
            this.error = ''
            var vm = this
            var url = '/api/exportReport'
            var students = this.selectedStudents
            if (students.length == 0)
                students = this.filteredStudents
            studentIds = []
            students.forEach((student) => {
                studentIds.push(student.id)
            })
            vm.month = vm.month || moment().format('DD MMMM YYYY')
            var postData = {
                month: vm.month,
                students: studentIds,
                categories: vm.selectedCategories,
                branches: vm.selectedBranches,
            }
            console.log(postData)
            var config = this.getHeaders()
            config.responseType = 'blob'
            this.$http.post(url, postData, config)
            .then(response => {
                this.loading = false
                var blob = new Blob([response.data])
                var link = document.createElement('a')
                link.href = window.URL.createObjectURL(blob)
                link.download = 'Report ' + vm.month + '.pdf'
                link.click()
            },
            error => {
                this.loading = false
                this.error = 'Error occured'
                console.log(error)
            })
        },
        showSummaryModal: function(){
            $('#summaryReportModal').modal('show')
        },
        showDetailModal: function(){
            $('#detailReportModal').modal('show')
        }
    },
    computed: {
        filteredStudents(){
            var vm = this
            return this.students.filter(student => {
                return (vm.selectedCategories.length == 0 || vm.selectedCategories.indexOf(student.category) != -1) &&
                (vm.selectedBranches.length == 0 || vm.selectedBranches.indexOf(student.branch) != -1)
            })
        }
    }
})