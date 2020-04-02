import pytest
from scicopia.parser.grobid import *

def test_remove_refs():
    source = "tests/data/grobid.xml"
    with open(source) as filename:
        xml = filename.read()
        xml = xml.replace(" <ref", "<ref")
        root = ET.fromstring(xml)
        del xml

        remove_refs(root)

def test_extract_title():
    source = "tests/data/grobid.xml"
    with open(source) as filename:
        xml = filename.read()
        xml = xml.replace(" <ref", "<ref")
        root = ET.fromstring(xml)
        del xml

        remove_refs(root)
        node = root.find(f"{TEI}teiHeader/{FILEDESC}")
        data = dict()
        title = node.find(f"{TEI}titleStmt")
        if not title is None:
            extract_title(title, data)


        assert "title" in data
        assert data["title"]=='OAPT: A Tool for Ontology Analysis and Partitioning'

def test_extract_authors():
    source = "tests/data/grobid.xml"
    with open(source) as filename:
        xml = filename.read()
        xml = xml.replace(" <ref", "<ref")
        root = ET.fromstring(xml)
        del xml

        remove_refs(root)
        node = root.find(f"{TEI}teiHeader/{FILEDESC}")
        data = dict()

        structured_info = node.find(f"{TEI}sourceDesc/{TEI}biblStruct")
        if not structured_info is None:
            authors = structured_info.findall(f"{TEI}analytic/{TEI}author")
            if authors:
                extract_authors(authors, data)

            
        assert "author" in data
        assert data["author"]== ['Alsayed Algergawy', 'Samira Babalou', 'Friederike Klan', 'Birgitta KÃ¶nig-Ries']

def test_extract_bibliographic_data():
    source = "tests/data/grobid.xml"
    with open(source) as filename:
        xml = filename.read()
        xml = xml.replace(" <ref", "<ref")
        root = ET.fromstring(xml)
        del xml

        remove_refs(root)
        biblio = root.find(f"{TEI}teiHeader/{FILEDESC}")
        bib = extract_bibliographic_data(biblio)

            
        assert "author" in bib
        assert bib["author"]== ['Alsayed Algergawy', 'Samira Babalou', 'Friederike Klan', 'Birgitta KÃ¶nig-Ries']
        assert "title" in bib
        assert bib["title"]=='OAPT: A Tool for Ontology Analysis and Partitioning'
        assert 'doi' in bib
        assert bib['doi']== '10.5441/002/edbt.2016.69'
        assert 'id' in bib
        assert bib['id']== '10.5441/002/edbt.2016.69'

def test_extract_text():
    source = "tests/data/grobid.xml"
    with open(source) as filename:
        xml = filename.read()
        xml = xml.replace(" <ref", "<ref")
        root = ET.fromstring(xml)
        del xml

        remove_refs(root)
        text = extract_text(root)

            
        assert text== "ABSTRACT\nOntologies are the backbone of the Semantic Web and facilitate sharing, integration, and discovery of data. However, the number of existing ontologies is vastly growing, which makes it is problematic for software developers to decide which ontology is suitable for their application. Furthermore, often, only a small part of the ontology will be relevant for a certain application. In other cases, ontologies are so large, that they have to be split up in more manageable chunks to work with them. To this end, in this demo, we present OAPT, an ontology analysis and partitioning tool. First, before a candidate input ontology is partitioned, OAPT analyzes it to determine, if this ontology is worth to be considered using a predefined set of criteria that quantify the semantic richness of the ontology. Once the ontology is investigated, we apply a seeding-based partitioning algorithm to partition it into a set of modules. Through the demonstration of OAPT we introduce the tool\'s capabilities and highlight its effectiveness and usability.\n\nINTRODUCTION\nOntologies are the backbone of the Semantic Web. By making information understandable for machines they enable integrating, searching, and sharing of information on the Web. The growing value of ontologies has resulted in the development of a large number of these. According to, at least 7000 ontologies exist on the Semantic Web, providing an unprecedented set of resources for developers of semantic applications. On the other hand, this large number of available ontologies makes it hard for software engineers to decide which ontology(ies) is (are) suitable for their needs. Even, if a developer settled on an ontology (or a set of ontologies), she is most often interested in a subset of concepts of the entire ontology, only. For example, the CHEBI ontology 1 , contains 46,477 fully annotated concepts describing chemical entities of which not all will be relevant to a specific application. Also, it might be necessary to split up large ontologies like CHEBI in more manageable chunks before feeding them to ontology matching tools or other applications.\n\nTo cope with these challenges, in this demo paper, we present OAPT, a tool for analyzing and partitioning ontologies. The tool allows the user to interactively investigate a candidate input ontology based on a predefined set of quality criteria. This will help to build trust for sharing and reusing ontologies. Once an ontology has been analyzed, the partitioning algorithm can be applied to partition the ontology into a set of disjoint modules. Our method to examine the ontology quality is based on the consistency and richness of the input ontology. First, a suitable reasoner is applied to the ontology to validate its consistency. It is clear that the way an ontology is engineered is largely based on the domain for which it is designed and modeled. Therefore, a measure for the semantic richness of an ontology should consider different aspects and its potential for knowledge representation. To this end, we then consider a set of structural, semantic, and syntactic metrics. The structural and syntactic criteria can be used to quantify the ontology design and its potential for knowledge representation, while the semantic-based criterion can be used to evaluate how instances are placed within the ontology.\n\nTo partition the analyzed ontology into a set of disjoint modules, we introduce a seeding-based clustering approach, called SeeCOnt. In particular, input ontologies are parsed and represented as concept graphs. A Ranker function is then used to rank ontology concepts exploiting the concept graph features. The highest ranked concepts are finally selected as cluster seeds (cluster heads). Each of these constitutes the initial concept of a resulting module. To assign the remaining concepts to their proper modules, we introduce a membership function. This reduces the complexity of the comparisons by comparing concepts with only seeds instead of all other concepts. Please note that this partitioning method is independent of the concrete application or a concrete subset of concepts a user is interested in. Rather, it relies on intrinsic ontology characteristics only. This allows, e.g., precomputation of the modules.\n\nThe rest of the paper is organized as follows. In Section 2 we present an overview of the proposed system, while in Section 3 we describe our demonstration scenario. Due to space restrictions, in this paper we provide only a glimpse of the techniques employed by OAPT. However, we refer to our full research paper for algorithmic details and for more elements of related work."

def test_parse():
    source = "tests/data/grobid.xml"
    with open(source) as data:
        for bib in parse(data):
            assert "author" in bib
            assert bib["author"]== ['Alsayed Algergawy', 'Samira Babalou', 'Friederike Klan', 'Birgitta KÃ¶nig-Ries']
            assert "title" in bib
            assert bib["title"]=='OAPT: A Tool for Ontology Analysis and Partitioning'
            assert 'doi' in bib
            assert bib['doi']== '10.5441/002/edbt.2016.69'
            assert 'id' in bib
            assert bib['id']== '10.5441/002/edbt.2016.69'    
            assert bib['fulltext']== "ABSTRACT\nOntologies are the backbone of the Semantic Web and facilitate sharing, integration, and discovery of data. However, the number of existing ontologies is vastly growing, which makes it is problematic for software developers to decide which ontology is suitable for their application. Furthermore, often, only a small part of the ontology will be relevant for a certain application. In other cases, ontologies are so large, that they have to be split up in more manageable chunks to work with them. To this end, in this demo, we present OAPT, an ontology analysis and partitioning tool. First, before a candidate input ontology is partitioned, OAPT analyzes it to determine, if this ontology is worth to be considered using a predefined set of criteria that quantify the semantic richness of the ontology. Once the ontology is investigated, we apply a seeding-based partitioning algorithm to partition it into a set of modules. Through the demonstration of OAPT we introduce the tool\'s capabilities and highlight its effectiveness and usability.\n\nINTRODUCTION\nOntologies are the backbone of the Semantic Web. By making information understandable for machines they enable integrating, searching, and sharing of information on the Web. The growing value of ontologies has resulted in the development of a large number of these. According to, at least 7000 ontologies exist on the Semantic Web, providing an unprecedented set of resources for developers of semantic applications. On the other hand, this large number of available ontologies makes it hard for software engineers to decide which ontology(ies) is (are) suitable for their needs. Even, if a developer settled on an ontology (or a set of ontologies), she is most often interested in a subset of concepts of the entire ontology, only. For example, the CHEBI ontology 1 , contains 46,477 fully annotated concepts describing chemical entities of which not all will be relevant to a specific application. Also, it might be necessary to split up large ontologies like CHEBI in more manageable chunks before feeding them to ontology matching tools or other applications.\n\nTo cope with these challenges, in this demo paper, we present OAPT, a tool for analyzing and partitioning ontologies. The tool allows the user to interactively investigate a candidate input ontology based on a predefined set of quality criteria. This will help to build trust for sharing and reusing ontologies. Once an ontology has been analyzed, the partitioning algorithm can be applied to partition the ontology into a set of disjoint modules. Our method to examine the ontology quality is based on the consistency and richness of the input ontology. First, a suitable reasoner is applied to the ontology to validate its consistency. It is clear that the way an ontology is engineered is largely based on the domain for which it is designed and modeled. Therefore, a measure for the semantic richness of an ontology should consider different aspects and its potential for knowledge representation. To this end, we then consider a set of structural, semantic, and syntactic metrics. The structural and syntactic criteria can be used to quantify the ontology design and its potential for knowledge representation, while the semantic-based criterion can be used to evaluate how instances are placed within the ontology.\n\nTo partition the analyzed ontology into a set of disjoint modules, we introduce a seeding-based clustering approach, called SeeCOnt. In particular, input ontologies are parsed and represented as concept graphs. A Ranker function is then used to rank ontology concepts exploiting the concept graph features. The highest ranked concepts are finally selected as cluster seeds (cluster heads). Each of these constitutes the initial concept of a resulting module. To assign the remaining concepts to their proper modules, we introduce a membership function. This reduces the complexity of the comparisons by comparing concepts with only seeds instead of all other concepts. Please note that this partitioning method is independent of the concrete application or a concrete subset of concepts a user is interested in. Rather, it relies on intrinsic ontology characteristics only. This allows, e.g., precomputation of the modules.\n\nThe rest of the paper is organized as follows. In Section 2 we present an overview of the proposed system, while in Section 3 we describe our demonstration scenario. Due to space restrictions, in this paper we provide only a glimpse of the techniques employed by OAPT. However, we refer to our full research paper for algorithmic details and for more elements of related work."


