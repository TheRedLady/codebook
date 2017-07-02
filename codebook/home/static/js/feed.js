function FeedViewModel(params) {
    self = this;
    self.userId = params.user_id;
    self.questionContainer = new QuestionContainer();
    self.answers = ko.observableArray([]);
    self.append = false;

    self.removeAnswer = removeAnswer;

    init();

    //---------

    function init() {
        $.ajax({
            url: RESTAPI_URLS.PROFILES + params.user_id + PROFILE_PAGES.FEED,
            type: METHODS.GET
        }).done(function(data) {
            data['questions'].forEach(function(question){
                self.questionContainer.questions.push(new QuestionListItemViewModel(question));
            });
            data['answers'].forEach(function(answer){
                self.answers.push(new AnswerListItemViewModel(answer));
            });
        });
    }


    function removeAnswer(answer) {
        answer.remove();
        self.answers.remove(answer);
    }
}

ko.components.register('feed-component', {
    template: { element: 'feed-template' },
    viewModel: FeedViewModel
});

ko.applyBindings();
