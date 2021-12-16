#!/usr/bin/env python

class Protobuf(object):
    _protos = dict()
    _names = dict()
    _abbr_names = dict()

    @classmethod
    def populate(cls):
        import re
        from .messages import OpenApiCommonMessages_pb2 as o1
        from .messages import OpenApiMessages_pb2 as o2

        for name in dir(o1) + dir(o2):
            if not name.startswith("Proto"):
                continue

            m = o1 if hasattr(o1, name) else o2
            klass = getattr(m, name)
            cls._protos[klass().payloadType] = klass
            cls._names[klass.__name__] = klass().payloadType
            abbr_name = re.sub(r'^Proto(OA)?(.*)', r'\2', klass.__name__)
            cls._names[abbr_name] = klass().payloadType
        return cls._protos

    @classmethod
    def get(cls, payload, fail=True, **params):
        if not cls._protos:
            cls.populate()

        if payload in cls._protos:
            return cls._protos[payload](**params)

        for d in [cls._names, cls._abbr_names]:
            if payload in d:
                payload = d[payload]
                return cls._protos[payload](**params)
        if fail:  # pragma: nocover
            raise IndexError("Invalid payload: " + str(payload))
        return None  # pragma: nocover

    @classmethod
    def get_type(cls, payload, **params):
        p = cls.get(payload, **params)
        return p.payloadType

    @classmethod
    def extract(cls, message):
        payload = cls.get(message.payloadType)
        payload.ParseFromString(message.payload)
        return payload
