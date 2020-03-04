from .object import *
from .constants import *
from . import validation


class Identified(SBOLObject):
    # The persistentIdentity property is OPTIONAL and has a data type of URI.
    # This URI serves to uniquely refer to a set of SBOL objects
    # that are different versions of each other.
    # An Identified object MUST be referred to
    # using either its identity URI or its persistentIdentity URI.
    _persistentIdentity = None

    # The displayId property is an OPTIONAL identifier
    # with a data type of String.
    # This property is intended to be an intermediate
    # between name and identity that is machine-readable,
    # but more human-readable than the full URI
    # of an identity. If the displayId property is used,
    # then its String value SHOULD be locally unique
    # (global uniqueness is not necessary)
    # and MUST be composed of only alphanumeric or underscore characters
    # and MUST NOT begin with a digit.
    _displayId = None

    # If the version property is used,
    # then it is RECOMMENDED that version numbering follow the conventions
    # of [semantic versioning](http://semver.org/),
    # particularly as implemented by [Maven](http://maven.apache.org/).
    # This convention represents versions as sequences
    # of numbers and qualifiers that are separated
    # by the characters '.' and '-' and are compared in lexicographical order
    # (for example, 1 < 1.3.1 < 2.0-beta).
    # For a full explanation, see the linked resources.
    _version = None

    # The wasDerivedFrom property is OPTIONAL and has a data type of URI.
    # An SBOL object with this property refers to another SBOL object
    # or non-SBOL resource from which this object was derived.
    # If the wasDerivedFrom property of an SBOL object A
    # that refers to an SBOL object B has an identical persistentIdentity,
    # and both A and B have a version,
    # then the version of B MUST precede that of A.
    # In addition, an SBOL object MUST NOT refer to itself
    # via its own wasDerivedFrom property
    # or form a cyclical chain of references via its wasDerivedFrom property
    # and those of other SBOL objects. For example, the reference chain
    # "A was derived from B and B was derived from A" is cyclical.
    _wasDerivedFrom = None

    # An Activity which generated this ComponentDefinition,
    # eg., a design process like codon-optimization
    # or a construction process like Gibson Assembly
    _wasGeneratedBy = None

    # The name property is OPTIONAL and has a data type of
    # String. This property is intended to be displayed to a human
    # when visualizing an Identified object. If an Identified object
    # lacks a name, then software tools SHOULD instead display the
    # object's displayId or identity. It is RECOMMENDED that software
    # tools give users the ability to switch perspectives between name
    # properties that are human-readable and displayId properties that
    # are less human-readable, but are more likely to be unique.
    _name = None

    # The description property is OPTIONAL and has a data type of String.
    # This property is intended to contain a more thorough
    # text description of an Identified object.
    _description = None

    def __init__(self, type_uri=SBOL_IDENTIFIED, uri=URIRef('example'),
                 version=VERSION_STRING):
        super().__init__(type_uri, uri)
        self._persistentIdentity = URIProperty(self, SBOL_PERSISTENT_IDENTITY,
                                               '0', '1', None, URIRef(uri))
        self._displayId = LiteralProperty(self, SBOL_DISPLAY_ID, '0', '1',
                                          [validation.sbol_rule_10204])
        self._version = LiteralProperty(self, SBOL_VERSION, '0', '1', None, version)
        self._name = LiteralProperty(self, SBOL_NAME, '0', '1', None)
        self._description = LiteralProperty(self, SBOL_DESCRIPTION, '0', '1', None)
        if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS.value) is True:
            self._displayId.set(uri)
            self._persistentIdentity.set(URIRef(os.path.join(getHomespace(), uri)))
            if Config.getOption(ConfigOptions.SBOL_TYPED_URIS.value) is True:
                if version != '':
                    self._identity.set(
                        URIRef(os.path.join(getHomespace(),
                                            self.getClassName(type_uri),
                                            uri, version))
                    )
                else:
                    self._identity.set(
                        URIRef(os.path.join(getHomespace(),
                                            self.getClassName(type_uri),
                                            uri))
                    )
            else:
                if version != '':
                    self._identity.set(
                        URIRef(os.path.join(getHomespace(), uri, version)))
                else:
                    self._identity.set(
                        URIRef(os.path.join(getHomespace(), uri)))
        elif hasHomespace():
            self._identity.set(URIRef(os.path.join(getHomespace(), uri)))
            self._persistentIdentity.set(
                URIRef(os.path.join(getHomespace(), uri)))
        # self._identity.validate() # TODO

    @property
    def persistentIdentity(self):
        return self._persistentIdentity.value

    @persistentIdentity.setter
    def persistentIdentity(self, new_persistentIdentity):
        self._persistentIdentity.set(new_persistentIdentity)

    @property
    def displayId(self):
        return self._displayId.value

    @displayId.setter
    def displayId(self, new_displayId):
        self._displayId.set(new_displayId)

    @property
    def version(self):
        return self._version.value

    @version.setter
    def version(self, new_version):
        self._version.set(new_version)

    @property
    def description(self):
        return self._description.value

    @description.setter
    def description(self, new_description):
        self._description.set(new_description)

    @property
    def name(self):
        return self._name.value

    @name.setter
    def name(self, new_name):
        self._name.set(new_name)

    def generate(self):
        raise NotImplementedError("Not yet implemented")

    def update_uri(self):
        """
        Recursively generates SBOL compliant ids for an object and all
        its owned objects, then checks to make sure that these ids are unique.
        :return: None
        """
        if self.parent is None:
            raise Exception('update_uri: Parent cannot be None')
        parent = self.parent
        if Config.getOption(ConfigOptions.SBOL_COMPLIANT_URIS.value) is True:
            # Form compliant URI for child object
            persistent_id = parent.properties[SBOL_PERSISTENT_IDENTITY][0]
            persistent_id = os.path.join(persistent_id, self.displayId)
            if len(parent.properties[SBOL_VERSION]) > 0:
                version = parent.properties[SBOL_VERSION][0]
            else:
                version = VERSION_STRING
            obj_id = os.path.join(persistent_id, version)
            # Reset SBOLCompliant properties
            self._identity.set(obj_id)
            self._persistentIdentity.set(persistent_id)
            # Check for uniqueness of URI in local object properties
            matches = parent.find_property_value(SBOL_IDENTIFIED, obj_id)
            if len(matches) > 0:
                raise SBOLError("Cannot update SBOL-compliant URI. The URI " +
                                self.identity + " is not unique",
                                SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE)
            for rdf_type, store in self.owned_objects.items():
                if rdf_type not in self._hidden_properties:
                    for nested_obj in store:
                        nested_obj.update_uri()
        # Check for uniqueness of URI in Document
        if parent.doc:
            matches = parent.doc.find_property_value(SBOL_IDENTITY, self.identity)
            if len(matches) > 0:
                raise SBOLError("Cannot update SBOL-compliant URI. "
                                "An object with URI " + self.identity +
                                " is already in the Document",
                                SBOLErrorCode.SBOL_ERROR_URI_NOT_UNIQUE)

    def copy(self, target_doc = None, target_namespace = None, version = None):

        def parseNamespace(uri):
            rlimit = uri.rfind('#') + 1
            if rlimit:
                return uri[:rlimit]
            rlimit = uri.rfind('/') + 1
            if rlimit:
                return uri[:rlimit]
            return ''

        new_obj = self.__class__()

        # Assign the new object to the target Document
        if target_doc:
            new_obj.doc = target_doc

        # This namespace map will be used later when copying namespaces over to
        # the new Document
        if self.doc:
            namespace_map = {ns: p for p, ns in self.doc._namespaces.items()}

        # Copy properties
        for property_uri, value_store in self.properties.items():
            new_obj.properties[property_uri] = value_store.copy()

            # Add a non-default namespace to the target document if not present
            # (This can happen when copying extension properties not in the
            # SBOL namespace, for example.)
            if self.doc and target_doc != None:
                property_namespace = URIRef(parseNamespace(property_uri))
                if property_namespace in namespace_map.keys():
                    prefix = namespace_map[property_namespace]
                    target_doc.addNamespace(property_namespace, prefix)

        # If caller specified a target_namespace argument, then import objects into this new namespace
        # This involves replacing the target_namespace in ReferenceObject URIs with the current Homespace
        # Don't overwrite namespaces for the wasDerivedFrom field, which points back to the original object
        if target_namespace:

            # Collect ReferencedObject attributes
            reference_properties = [p for p in new_obj.__dict__.values() if isinstance(p, ReferencedObject)]

            # These URIProperty attributes should be treated like ReferencedObject attributes
            if '_identity' in new_obj.__dict__.keys():
                reference_properties.append(new_obj.__dict__['_identity'])
            if '_persistentIdentity' in new_obj.__dict__.keys():
                reference_properties.append(new_obj.__dict__['_persistentIdentity'])

            for reference_property in reference_properties:
                if reference_property._upperBound == '1':
                    values = [reference_property.value]
                else:
                    values = reference_property.value
                for i_val, val in enumerate(values):
                    if target_namespace in val:
                        replacement_target = target_namespace
                        replacement = getHomespace()
                        new_val = val.replace(replacement_target, replacement)
                        values[i_val] = new_val
                if reference_property._upperBound == '1':
                    reference_property.value = values[0]
                else:
                    reference_property.value = values
                print(reference_property._rdf_type, reference_property.value)
            # if target_namespace:
            #     for i_val, val in enumerate(new_obj.properties[property_uri]):
            #         if target_namespace in val:
            #             if property_uri == SBOL_PERSISTENT_IDENTITY:
            #                 pass
            #             elif self.dict:
            #                 referenced_object = 
            #                 # If the value is an SBOL-typed URI, replace both the namespace and class name
            #                 class_name = parseClassName(val)
            #                 replacement_target = target_namespace + '/' + class_name
                            
            #                 # If not an sbol typed URI, then just replace the namespace
            #                 if not replacement_target in val:
            #                     replacement_target = target_namespace

            #             # If SBOL-typed URIs are enabled, replace with
            #             replacement = getHomespace()
            #             new_val = val.replace(replacement_target, replacement)
            #             if type(val) == URIRef:
            #                 new_val = URIRef(new_val)
            #             new_obj.properties[property_uri][i_val] = new_val


        return new_obj

'''
    Identified& Identified::copy(Document* target_doc, string ns, string version)
{
    // Call constructor for the copy
    string new_obj_type;
    if (SBOL_DATA_MODEL_REGISTER.find(this->type) != SBOL_DATA_MODEL_REGISTER.end())
        new_obj_type = this->type;
    else
        new_obj_type = SBOL_IDENTIFIED;
    Identified& new_obj = (Identified&)SBOL_DATA_MODEL_REGISTER[ new_obj_type ]();

    // Assign the new object to the target Document (null for non-TopLevel objects)
    if (target_doc)
        new_obj.doc = target_doc;

    new_obj.type = this->type;

    // Copy properties
    for (auto i_store = properties.begin(); i_store != properties.end(); ++i_store)
    {
        string store_uri = i_store->first;
        vector < string > property_store = i_store->second;
        vector < string > property_store_copy = property_store;   // Copy properties

        // Add the property namespace to the target document if not present
        if (doc)
        {
            string property_ns = parseNamespace(store_uri);
            for (auto i_document_ns : this->doc->namespaces)
            {
                string prefix = i_document_ns.first;
                string document_ns = i_document_ns.second;
                if (!document_ns.compare(property_ns))
                    target_doc->namespaces[prefix] = property_ns;
            }
        }

        // If caller specified a namespace argument, then replace namespace in URIs
        // Don't overwrite namespaces for the wasDerivedFrom field, which points back to the original object
        if (ns.compare("") != 0 && store_uri.compare(SBOL_WAS_DERIVED_FROM) != 0)
        {
            string old_ns = ns;
            for (int i_property_val = 0; i_property_val < property_store_copy.size(); ++i_property_val)
            {
                string property_val = property_store_copy[i_property_val];
                if (property_val[0] == '<')
                {
                    string uri = property_val.substr(1, property_val.length() - 2);  // Removes flanking < and > from uri
                    size_t pos = 0;
                    pos = property_val.find(old_ns, pos);
                    if (pos != std::string::npos)
                    {
                        // Copy object reference to new namespace and insert type
                        string replace_target;
                        string replacement;
                        string class_name;
                        if (store_uri == SBOL_PERSISTENT_IDENTITY)
                        {
                            class_name = parseClassName(new_obj.getTypeURI());
                            replace_target = old_ns + "/" + class_name;
                            pos = property_val.find(replace_target, 0);
                            if (pos == std::string::npos)
                            {
                                replace_target = old_ns;
                                pos = property_val.find(replace_target, 0);
                            }
                        }
                        else
                        {
                            SBOLObject* referenced_obj = doc->find(uri);  // Distinguish between a referenced object versus an ontology URI
                            if (referenced_obj)
                            {
                                class_name = parseClassName(referenced_obj->getTypeURI());
                                replace_target = old_ns + "/" + class_name;
                                pos = property_val.find(replace_target, 0);
                                if (pos == std::string::npos)
                                {
                                    replace_target = old_ns;
                                    pos = property_val.find(replace_target, 0);
                                }
                            }
                        }
                        // Construct replacement token
                        if (Config::getOption("sbol_compliant_uris") == "True" && Config::getOption("sbol_typed_uris") == "True")
                        {
                            replacement = getHomespace() + "/" + class_name;
                        }
                        else
                        {
                            replacement = getHomespace();
                        }
                        property_val.erase(pos, replace_target.size());
                        property_val.insert(pos, replacement);
                        property_store_copy[i_property_val] = property_val;
                    }
                }
            }
        }
        new_obj.properties[store_uri] = property_store_copy;
    }

    // Set version

    if (version != "")
        new_obj.version.set(version);
    else if (version == "" && ns == "")
    {
        if (this->version.size() > 0)
            if (this->doc != NULL && this->doc == target_doc)  // In order to create a copy of the object in this Document, it's version must be incremented
                new_obj.version.incrementMajor();
            else
            {
                new_obj.version.set(this->version.get());  // Copy this object's version if the user doesn't specify a new one
            }
    }
    else if (version == "" && ns != "")
    {
        if (this->version.size() > 0)
            {
                new_obj.version.set(this->version.get());  // Copy this object's version if the user doesn't specify a new one
            }
    }

    string id;
    if (Config::getOption("sbol_compliant_uris") == "True" && this->version.size() > 0)
        id = new_obj.persistentIdentity.get() + "/" + new_obj.version.get();
    else
        id = new_obj.persistentIdentity.get();
    new_obj.identity.set(id);

    // Copy wasDerivedFrom
    if (this->identity.get() != new_obj.identity.get())
        new_obj.wasDerivedFrom.set(this->identity.get());  // When generating a new object from an old, point back to the copied object
    else if (this->wasDerivedFrom.size() > 0)
        new_obj.wasDerivedFrom.set(this->wasDerivedFrom.get()); // When cloning an object, don't overwrite the wasDerivedFrom

    for (auto i_store = owned_objects.begin(); i_store != owned_objects.end(); ++i_store)
    {
        string store_uri = i_store->first;
        if (target_doc && std::find(hidden_properties.begin(), hidden_properties.end(), store_uri) != hidden_properties.end() )
            continue;

        vector < SBOLObject* >& object_store = i_store->second;
        for (auto i_obj = object_store.begin(); i_obj != object_store.end(); ++i_obj)
        {
            Identified& child_obj = (Identified&)**i_obj;

            // Recurse into child objects and copy.  This should be after all other object properties are set, to ensure proper generation of new URIs with updated namespace and version
            Identified& child_obj_copy = child_obj.copy(target_doc, ns, version);
            new_obj.owned_objects[store_uri].push_back((SBOLObject*)&child_obj_copy);  // Copy child object
            child_obj_copy.parent = &new_obj;
            child_obj_copy.update_uri();
        }
    }
    return new_obj;
};
'''