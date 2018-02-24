var app = new Vue({
        el: '#app',
        data: {
            heading:'Attendance',
            token: Cookies.get('auth_token'),
            is_admin: (Cookies.get('is_admin')=='true'),
            students: [],
            error: '',
            message: '',
            loading: '',
            timeFormat: '',
            attendanceDate: moment(),
            displayDateString: moment().format('dddd, Do MMMM'),
            viewOnly: false,
            nextIsFuture: true,
        },
        created: function(){
            console.log('stating');
            this.loadStudents();
        },
        methods: {
            logout: function(){
                Cookies.remove('auth_token');
                window.location = '/';
            },
            loadStudents: function(){
                this.loading = 'Loading students...'
                var token = this.token;
                console.log('token', token);
                this.$http.get('/api/student',this.getHeaders())
                .then(data => {
                        console.log(data);
                        this.students = data.body.students
                        if(this.students.length == 0){
                        if(data.body.message)
                                this.message = data.body.message;
                            else
                                this.message = 'No students';
                        }else{
                            this.message = '';
                        }
                        console.log(this.message);
                        this.loading = '';
                        this.getAttendance();
                    },error => {
                        this.error = error.body.message;
                        console.log(error);
                        this.loading = '';
                    });
            },
            getHeaders: function(){
                return {headers: { Authorization: 'Basic ' +  this.token}};
            },
            getAttendance: function(){
                this.loading = 'Loading attendance...'
                var token = this.token
                var vm = this
                var url = '/api/attendance/'+this.attendanceDate.format('DDMMYYYY')
                this.$http.get(url, vm.getHeaders())
                .then(data => {
                        console.log(data);
                        vm.students.forEach(function(student, stdi){
                            student.in = undefined;
                            student.out = undefined;
                            student.comment = undefined;
                            data.body.attendance.forEach(function(item, index){
                                if(student.id == item.student.id){
                                    console.log(student,item,'matched');
                                    student.in = item.punchIn;
                                    student.out = item.punchOut;
                                    student.comment = item.comments;
                                    vm.$set(vm.students, stdi, student);
                                }
                            })
                        });
                        this.loading = '';
                    },error => {
                        console.log(error);
                        this.loading = '';
                        this.message = error.data.message;
                    });
            },
            saveAttendaceData: function(student, what){
                if(what != 'in' && what != 'out' && what != 'comment') return;
                
                var updatedStd = student;
                var postData = {};

                if(what == 'in'){
                    updatedStd.in = moment().format('HH:mm:ss');
                    postData.in = updatedStd.in;
                }
                else if(what == 'out'){
                    updatedStd.out = moment().format('HH:mm:ss');
                    postData.out = updatedStd.out;
                }
                else if(what == 'comment'){
                    postData.comment = updatedStd.comment;
                }

                var url = '/api/attendance/'+moment(this.attendanceDate).format('DDMMYYYY')+'/'+student.id+'/'+what
                console.log('url',url);
                console.log('postData',postData);
                var vm = this;
                vm.$set(vm.students, vm.students.indexOf(student), updatedStd);
                //ajax request to punch in the student
                vm.$http.post(url, postData, vm.getHeaders())
                .then(response => {
                    if(response.body.status == 'success'){
                        console.log('saved')
                    }else{
                        // undo the changes in ui
                       var redoUpdatedStd = updatedStd;
                        if(what == 'in'){
                            redoUpdatedStd.in = undefined;
                        }
                        else if(what == 'out'){
                            redoUpdatedStd.out = undefined;
                        }
                        else if(what == 'comment'){
                            redoUpdatedStd.comment = undefined;
                        }
                        vm.$set(vm.students, vm.students.indexOf(updatedStd), redoUpdatedStd);
                    }
                }, error => {
                    console.log(error);
                    var redoUpdatedStd = updatedStd;
                    redoUpdatedStd.in = undefined;
                    this.$set(this.students, this.students.indexOf(updatedStd), redoUpdatedStd);
                });
            },
            punchOut: function(student){
                var updatedStd = student;
                if(!student.out)
                    updatedStd.out = moment().format('HH:mm:ss');
                else
                    updatedStd.out = undefined;
                this.$set(this.students, this.students.indexOf(student), updatedStd);
                console.log(this.students);
            },
            getTimeString: function(datetime){
                return moment(datetime,['HH:mm:ss']).format('hh:mm:ss A');
            },
            nextDay: function(){
                console.log('nextDay');
                this.attendanceDate = moment(this.attendanceDate).add(1, 'day');
                var today = moment()
                if(today.diff(this.attendanceDate,'days')==0)
                    this.viewOnly = false;    
                this.getAttendance();
            },
            previousDay: function(){
                console.log('preDay');
                this.attendanceDate = moment(this.attendanceDate).subtract(1, 'day');
                this.viewOnly = true;
                this.getAttendance();
            }
        },
        watch:{
            token: function(){
                if(!this.token)
                    window.location = '/';
            },
            attendanceDate: function(){
                var currAttendance = moment(this.attendanceDate)
                currAttendance.add(1,'day')
                var today = moment()
                this.nextIsFuture = currAttendance.isAfter(today)
                console.log(this.nextIsFuture);
            }
        },
        computed:{
            currentAttendanceDate:function(){
                return this.attendanceDate.format('dddd, Do MMMM');;
            }
        }
    });