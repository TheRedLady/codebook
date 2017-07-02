function AnswerListItemViewModel(data) {
    var self = this;
    self.answerId = data['id'];
    self.author = new AuthorViewModel(data['author']);
    self.votes = ko.observable(data['votes']);
    self.content = data['content'];
    self.datePublished = data['created'];
    self.voted = ko.observable(null);
    self.isTopAnswer = data['is_top_answer'];
    self.questionUrl = data['question']['url'];

    self.remove = remove;

    //-----

    function remove() {
        $.ajax({
            url: RESTAPI_URLS.ANSWERS + self.answerId + '/',
            method: METHODS.DELETE,
        });
    }

    return self;
};
