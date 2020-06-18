'''
Interface classes for set/get/update/delete tags refering to another table via foreign key
'''
from abc import ABC, abstractmethod

class TagInterface(ABC):
    '''
    Defines the interface for set/get/update/delete tags
    '''

    @abstractmethod
    def setResultTags(self, resultId, tagDictionary):
        '''
        Set, update, or delete tags on the specified Result:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param resultId: int of the Result to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        pass
        
    @abstractmethod
    def getResultTags(self, resultId, tagNames):       
        '''
        Retrieve tags on the specified Result:
        :param resultId: int of the Result to query
        :param tagNames: list of strings
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        pass
        
    @abstractmethod
    def setPlotTags(self, plotId, tagDictionary):
        '''
        Set, update, or delete tags on the specified Plot:
        Tag name keys evaluating to False are ignored.
        Empty string values are stored, but None and False values cause a tag to be deleted.
        :param plotId: int of the Plot to update.
        :param tagDictionary: dictionary of tag names and value strings.
        '''
        pass
        
    @abstractmethod
    def getPlotTags(self, plotId, tagNames):       
        '''
        Retrieve tags on the specified Plot:
        :param plotId: int of the Plot to query
        :param tagNames: list of strings
        :return dictionary of dictionary of tag names and value strings, or None if the tag was not found.
        '''
        pass
